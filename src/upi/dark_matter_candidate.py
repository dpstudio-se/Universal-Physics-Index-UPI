"""Conditional octave scaling and nonrelativistic recoil; never particle identification.

SI internally. Public numerical records are DER under their declared assumptions.
The two physical identifications are separate HYP graph nodes.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from decimal import Decimal, localcontext
from fractions import Fraction

from .constants import C, E, H
from .physics import energy_from_frequency, frequency_from_mass, mass_from_frequency

EV_J = E
GEV_KG = EV_J * 1e9 / C**2
KEV_J = EV_J * 1e3
U_KG = 1.66053906892e-27  # CODATA 2022; standard uncertainty 5.2e-37 kg
ELECTRON_KG = 9.1093837139e-31  # CODATA 2022
XE_ATOMIC_U = {129: 128.9047808611, 131: 130.90508406, 132: 131.9041550856,
               136: 135.907214484}


def nonnegative(x: float, name: str) -> None:
    if isinstance(x, bool) or not math.isfinite(x) or x < 0:
        raise ValueError(f"{name} must be finite and nonnegative")


def positive(x: float, name: str) -> None:
    nonnegative(x, name)
    if x == 0:
        raise ValueError(f"{name} must be positive")


def frequency_chain(f0: str = "7.834", n: int = 84) -> dict:
    """Path A: 80-digit decimal SI; path B: exact rational inverse + existing float API.

    Strings retain input decimal precision. f and E are exact finite decimals for
    these inputs; the rational fraction preserves the nonterminating mass exactly.
    """
    if isinstance(n, bool) or not isinstance(n, int) or not -1024 <= n <= 1024:
        raise ValueError("n must be an integer in [-1024, 1024]")
    with localcontext() as ctx:
        ctx.prec = 80
        start = Decimal(f0)
        if not start.is_finite() or start < 0:
            raise ValueError("frequency must be finite and nonnegative")
        h, c, ev = Decimal("6.62607015e-34"), Decimal("299792458"), Decimal("1.602176634e-19")
        f = start * Decimal(2)**n
        energy = h*f
        mass = energy/c**2
        energy_ev = energy/ev
        reconstructed = mass*c**2/h
        # Independently constructed rational constants, not converted float results.
        rh = Fraction(662607015, 10**42)
        rc = 299792458
        rf = Fraction(f0) * Fraction(2)**n
        rm = rf*rh/rc**2
        back = rm*rc**2/rh
        float_f = float(f)
        if not math.isfinite(float_f):
            raise ValueError("frequency exceeds independent float verification domain")
        float_mass = mass_from_frequency(float_f) if float_f else 0.0
        return {"status": "DER", "verification_type": "software_test", "f0_Hz": f0,
                "N": n, "f_N_Hz": str(f), "energy_J": str(energy),
                "mass_equivalent_kg": str(mass), "energy_eV": str(energy_ev),
                "mass_equivalent_GeV_c2": str(energy_ev/Decimal(10)**9),
                "mass_exact_rational_kg": f"{rm.numerator}/{rm.denominator}",
                "decimal_frequency_residual_Hz": str(reconstructed-f),
                "rational_inverse_residual_Hz": str(back-rf),
                "existing_api_mass_relative_residual": (float_mass/float(mass)-1) if mass else 0,
                "existing_api_energy_relative_residual": (energy_from_frequency(float_f)/float(energy)-1) if energy else 0,
                "existing_api_inverse_relative_residual": (frequency_from_mass(float_mass)/float_f-1) if float_f else 0,
                "scope": "Energy equivalent only; N mechanism and particle identity remain HYP"}


def target_mass(isotope: int = 131, binding_energy_ev: float = 0.0) -> float:
    """Nuclear mass = atomic mass - 54 m_e + B_e/c².

    Default neglects total electron binding (explicit approximation); never claim
    the resulting many digits are an exact measured nuclear mass.
    """
    nonnegative(binding_energy_ev, "electron binding energy")
    if isinstance(isotope, bool) or isotope not in XE_ATOMIC_U:
        raise ValueError("unsupported xenon isotope")
    return XE_ATOMIC_U[isotope]*U_KG - 54*ELECTRON_KG + binding_energy_ev*EV_J/C**2


def reduced_mass(chi: float, nucleus: float) -> float:
    positive(chi, "candidate mass in kg")
    positive(nucleus, "target mass in kg")
    return 1/(1/chi + 1/nucleus)


def recoil(chi: float, nucleus: float, speed: float, cos_theta: float = -1.0) -> dict:
    """CM scattering angle. q²=2(mu v)²(1-cos(theta)); E_R=q²/(2m_A)."""
    nonnegative(speed, "lab speed m/s")
    if speed >= 0.01*C:
        raise ValueError("outside declared nonrelativistic domain v < 0.01c")
    if not math.isfinite(cos_theta) or not -1 <= cos_theta <= 1:
        raise ValueError("CM angle cosine outside [-1,1]")
    mu = reduced_mass(chi, nucleus)
    q = mu*speed*math.sqrt(2*(1-cos_theta))
    er = q*q/(2*nucleus)
    return {"status": "DER", "speed_km_s": speed/1000, "recoil_keV": er/KEV_J,
            "q_kg_m_s": q, "q_MeV_c": q*C/(EV_J*1e6), "mu_kg": mu,
            "mu_GeV_c2": mu/GEV_KG, "cos_theta_CM": cos_theta,
            "assumptions": "elastic two-body scattering; stationary free nucleus; v<0.01c; H_DM conditional"}


def inverse_speed(recoil_j: float, chi: float, nucleus: float) -> float:
    """Independent lab conservation inverse for collinear backscatter.

    Target final speed u=sqrt(2 E_R/m_A); v=u*(m_chi+m_A)/(2m_chi).
    This is minimum incident speed, not the speed of a uniquely identified event.
    """
    nonnegative(recoil_j, "recoil J")
    positive(chi, "candidate kg")
    positive(nucleus, "target kg")
    return math.sqrt(2*recoil_j/nucleus)*(1+nucleus/chi)/2


@dataclass(frozen=True)
class Halo:
    """Illustrative truncated Maxwellian, not a measured posterior."""

    rho_GeV_cm3: float = 0.3  # means GeV/c² per cm³
    v0_m_s: float = 220000.0
    vesc_m_s: float = 544000.0
    earth_m_s: float = 232000.0

    def __post_init__(self) -> None:
        for name in ("rho_GeV_cm3", "v0_m_s", "vesc_m_s"):
            positive(getattr(self, name), name)
        nonnegative(self.earth_m_s, "earth_m_s")
        if self.earth_m_s >= self.vesc_m_s or self.vesc_m_s+self.earth_m_s >= .01*C:
            raise ValueError("require v_E < v_esc and support below 0.01c")


def mean_inverse_speed(vmin: float, halo: Halo) -> float:
    """eta = integral f_lab(v)/|v| d³v, SI s/m, normalized truncated Maxwellian."""
    nonnegative(vmin, "vmin")
    v0, ve, esc = halo.v0_m_s, halo.earth_m_s, halo.vesc_m_s
    z = esc/v0
    norm = math.erf(z)-2*z*math.exp(-z*z)/math.sqrt(math.pi)
    if vmin >= esc+ve:
        return 0.0
    if ve == 0:
        return 2*(math.exp(-(vmin/v0)**2)-math.exp(-z*z))/(norm*math.sqrt(math.pi)*v0)
    x, y = vmin/v0, ve/v0
    if vmin < esc-ve:
        value = math.erf(x+y)-math.erf(x-y)-4*y*math.exp(-z*z)/math.sqrt(math.pi)
    else:
        value = math.erf(z)-math.erf(x-y)-2*(z-x+y)*math.exp(-z*z)/math.sqrt(math.pi)
    return max(0.0, value/(2*norm*ve))


def helm_squared(q: float, isotope: int = 131, radius_fm: float | None = None,
                 skin_fm: float = .9) -> float:
    """Helm uniform-sphere Gaussian convolution: R1²=R²-5s²; R=1.2 A^(1/3) fm.

    Radius choice is a declared phenomenological benchmark, not a fitted Xe radius.
    """
    nonnegative(q, "momentum")
    positive(skin_fm, "skin fm")
    if isinstance(isotope, bool) or isotope not in XE_ATOMIC_U:
        raise ValueError("unsupported isotope")
    radius = 1.2*isotope**(1/3) if radius_fm is None else radius_fm
    positive(radius, "radius fm")
    if radius**2 <= 5*skin_fm**2:
        raise ValueError("Helm effective radius must be real positive")
    hbar = H/(2*math.pi)
    x = q*math.sqrt(radius**2-5*skin_fm**2)*1e-15/hbar
    qs = q*skin_fm*1e-15/hbar
    sphere = 1-x*x/10+x**4/280 if abs(x) < 1e-3 else 3*(math.sin(x)-x*math.cos(x))/x**3
    return sphere*sphere*math.exp(-qs*qs)


DEFAULT_HALO = Halo()


def rate_coefficient(er_keV: float, chi: float, halo: Halo = DEFAULT_HALO, isotope: int = 131,
                     radius_fm: float | None = None, skin_fm: float = .9) -> dict:
    """dR/dE_R = coefficient * sigma_A(0) [m²], per kg day keV.

    Spin-independent elastic contact benchmark, pure isotope, unknown nuclear
    cross section is left symbolic. No efficiency, exposure or energy smearing.
    """
    nonnegative(er_keV, "recoil keV")
    nucleus = target_mass(isotope)
    mu = reduced_mass(chi, nucleus)
    er = er_keV*KEV_J
    q = math.sqrt(2*nucleus*er)
    vmin = inverse_speed(er, chi, nucleus)
    eta = mean_inverse_speed(vmin, halo)
    f2 = helm_squared(q, isotope, radius_fm, skin_fm)
    rho = halo.rho_GeV_cm3*GEV_KG*1e6
    coefficient = rho/(2*chi*mu**2)*f2*eta*86400*KEV_J
    return {"status": "DER", "energy_keV": er_keV, "vmin_km_s": vmin/1000,
            "form_factor_squared": f2, "eta_s_m": eta,
            "rate_per_sigma_A_m2": coefficient, "unit": "events kg^-1 day^-1 keV^-1 m^-2",
            "cross_section": "sigma_A(0) in m² remains an unknown parameter",
            "detector_response": "not applied"}
