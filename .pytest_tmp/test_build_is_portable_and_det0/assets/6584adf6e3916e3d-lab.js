(() => {
  'use strict';
  const byId = (id) => document.getElementById(id);
  const form = byId('lab-form');
  const fields = ['frequency', 'g27', 'volume', 'lambda27', 'curvature', 'errors'];
  const outputs = ['energy', 'mass', 'inverse', 'residual', 'g4', 'lambda4'];
  let report = null;
  function format(value) {
    if (value === 0) return '0';
    if (Math.abs(value) < 0.001 || Math.abs(value) >= 1e7) return value.toExponential(7);
    return Number(value.toPrecision(9)).toLocaleString('sv-SE', {maximumSignificantDigits: 9});
  }
  function update() {
    byId('export-status').textContent = '';
    try {
      report = null;
      const inputs = Object.fromEntries(fields.map((id) => [id, byId(id).valueAsNumber]));
      const result = UPILab.calculate(inputs);
      const values = [result.bridge.energy_J, result.bridge.energy_equivalent_mass_kg,
        result.bridge.inverse_Hz, result.bridge.relative_error, result.geometry.g4_L2,
        result.geometry.lambda4_inverse_L2];
      outputs.forEach((id, i) => { byId(id).textContent = format(values[i]); });
      byId('error-count').textContent = inputs.errors;
      byId('bits').replaceChildren(...Array.from({length: 24}, (_, i) => {
        const bit = document.createElement('span');
        bit.className = i < inputs.errors ? 'bit flipped' : 'bit';
        return bit;
      }));
      byId('code-result').textContent = result.golay.within_guarantee
        ? `${inputs.errors} bitfel · Inom garantin för entydig korrigering.`
        : `${inputs.errors} bitfel · Utanför korrigeringsgarantin. Ingen säker återställning följer av gränsen.`;
      report = result;
      byId('form-error').hidden = true;
      byId('export').disabled = false;
    } catch (error) {
      outputs.forEach((id) => { byId(id).textContent = '—'; });
      byId('code-result').textContent = 'Korrigera inmatningen för att beräkna resultat.';
      byId('bits').replaceChildren();
      byId('form-error').textContent = error.message;
      byId('form-error').hidden = false;
      byId('export').disabled = true;
    }
  }
  form.addEventListener('submit', (event) => event.preventDefault());
  form.addEventListener('input', update);
  form.addEventListener('reset', () => setTimeout(update, 0));
  document.querySelectorAll('[data-frequency]').forEach((button) => {
    button.addEventListener('click', () => { byId('frequency').value = button.dataset.frequency; update(); });
  });
  byId('export').addEventListener('click', () => {
    update();
    if (!report) return;
    const blob = new Blob([JSON.stringify(report, null, 2) + '\n'], {type: 'application/json'});
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'teax-lab-v1.json';
    document.body.append(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    byId('export-status').textContent = 'Export skapad med parametrar, resultat och antaganden.';
  });
  const settingsKey = 'upi-lab-settings-v1';
  const settingsStatus = byId('settings-status');
  function applySettings(saved) {
    if (!saved || saved.version !== '1.0.0') throw new Error('Okänd inställningsversion.');
    const validated = UPILab.calculate(saved.inputs);
    fields.forEach((id) => { byId(id).value = validated.inputs[id]; });
    update();
  }
  byId('save-settings').addEventListener('click', () => {
    update();
    if (!report) { settingsStatus.textContent = 'Korrigera parametrarna innan du sparar.'; return; }
    try {
      localStorage.setItem(settingsKey, JSON.stringify({version: report.version, inputs: report.inputs}));
      settingsStatus.textContent = 'Parametrar sparade på den här enheten.';
    } catch {
      settingsStatus.textContent = 'Webbläsaren tillåter inte lagring. Använd JSON-export i stället.';
    }
  });
  byId('forget-settings').addEventListener('click', () => {
    try {
      localStorage.removeItem(settingsKey);
      settingsStatus.textContent = 'Sparade parametrar rensade. Aktuella värden är kvar tills du återställer.';
    } catch {
      settingsStatus.textContent = 'Webbläsaren tillåter inte åtkomst till lagringen.';
    }
  });
  byId('import-settings').addEventListener('change', async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    try {
      if (file.size > 100000) throw new Error('Filen får vara högst 100 kB.');
      applySettings(JSON.parse(await file.text()));
      settingsStatus.textContent = 'Parametrar inlästa. Spara om de ska behållas efter omladdning.';
    } catch {
      settingsStatus.textContent = 'Filen kunde inte läsas. Välj en giltig UPI v1-export under 100 kB. Befintliga parametrar behålls.';
    } finally {
      event.target.value = '';
    }
  });
  update();
  try {
    const saved = localStorage.getItem(settingsKey);
    if (saved) { applySettings(JSON.parse(saved)); settingsStatus.textContent = 'Dina sparade parametrar har lästs in.'; }
  } catch {
    settingsStatus.textContent = 'Sparade inställningar kunde inte läsas. Standardvärden visas.';
  }
})();
