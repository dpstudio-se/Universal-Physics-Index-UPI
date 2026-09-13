"""verification_type: software_test; SFTP double, not external hosting evidence."""

import io
import json
import stat
from types import SimpleNamespace
from zipfile import ZipFile

import pytest

from upi.site import MARKER, build_archive, build_site, publish, remote_parts


class MemorySFTP:
    def __init__(self):
        self.files = {}
        self.dirs = set()
        self.symlinks = set()
        self.events = []
        self.corrupt = False
        self.atomic_supported = True

    def lstat(self, name):
        if name in self.symlinks:
            return SimpleNamespace(st_mode=stat.S_IFLNK)
        if name in self.files:
            return SimpleNamespace(st_mode=stat.S_IFREG)
        if name in self.dirs:
            return SimpleNamespace(st_mode=stat.S_IFDIR)
        raise FileNotFoundError(name)

    def mkdir(self, name):
        self.dirs.add(name)

    def open(self, name, mode):
        if mode == "rb":
            if name not in self.files:
                raise FileNotFoundError(name)
            return io.BytesIO(self.files[name])
        owner = self

        class Writer(io.BytesIO):
            def close(self):
                owner.files[name] = self.getvalue() + (b"corrupt" if owner.corrupt else b"")
                super().close()

        return Writer()

    def rename(self, source, target):
        assert target not in self.files
        self.files[target] = self.files.pop(source)
        self.events.append(target)

    def posix_rename(self, source, target):
        if not self.atomic_supported:
            raise OSError("Atomic rename unsupported")
        self.files[target] = self.files.pop(source)
        self.events.append(target)


def test_build_is_portable_and_deterministic(tmp_path):
    first = build_site(tmp_path)
    assert first == build_site(tmp_path)
    html = first["index.html"].decode()
    assert '/static/' not in html
    assert 'href="/lab"' not in html
    assert 'href="/"' not in html
    assert 'href="#settings"' in html
    assert 'DINA INSTÄLLNINGAR' in html
    assert json.loads(first["manifest.json"])["application"] == "upi-static-laboratory"
    assert all((tmp_path / name).read_bytes() == data for name, data in first.items())


def test_archive_refreshes_only_current_build_and_excludes_unrelated_files(tmp_path):
    output = tmp_path / "upi"
    files = build_site(output)
    (output / ".env").write_text("test-only secret sentinel", encoding="utf-8")
    archive_path = tmp_path / "site.zip"
    build_archive(files, archive_path)
    changed = {**files, "index.html": files["index.html"] + b"\n<!-- updated -->"}
    build_archive(changed, archive_path)
    with ZipFile(archive_path) as archive:
        assert set(archive.namelist()) == {"upi/" + name for name in changed}
        assert archive.testzip() is None
        for name, raw in changed.items():
            assert archive.read("upi/" + name) == raw


@pytest.mark.parametrize("path", ["/", "", "../upi", "/upi", "www/../upi", "upi//x", "upi\\x"])
def test_remote_directory_cannot_escape_home(path):
    with pytest.raises(ValueError):
        remote_parts(path)


def test_publish_switches_index_last_and_preserves_previous(tmp_path):
    files = build_site(tmp_path)
    sftp = MemorySFTP()
    old = (MARKER + "old version").encode()
    sftp.files["upi/index.html"] = old
    backup = publish(sftp, files, "upi")
    assert sftp.files[backup + "/previous-index.html"] == old
    assert sftp.files["upi/index.html"] == files["index.html"]
    assert sftp.events[-1] == "upi/index.html"
    publish(sftp, files, "upi")  # repeated update reuses verified immutable assets


@pytest.mark.parametrize("failure", ["unowned", "symlink", "corruption", "atomic"])
def test_failure_preserves_existing_site(tmp_path, failure):
    sftp = MemorySFTP()
    old = (MARKER + "old version").encode()
    if failure == "unowned":
        old = b"unrelated website"
    if failure == "symlink":
        sftp.symlinks.add("upi")
    if failure == "corruption":
        sftp.corrupt = True
    if failure == "atomic":
        sftp.atomic_supported = False
    sftp.files["upi/index.html"] = old
    with pytest.raises((ValueError, OSError)):
        publish(sftp, build_site(tmp_path), "upi")
    assert sftp.files["upi/index.html"] == old
