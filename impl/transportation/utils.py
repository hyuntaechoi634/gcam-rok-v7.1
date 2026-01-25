# utils.py
from __future__ import annotations

from pathlib import Path
import os
from typing import Tuple, List, Dict, Iterable, Optional

import pandas as pd
import xml.etree.ElementTree as ET
from xml.dom import minidom


# =============================================================================
# General numeric helpers
# =============================================================================

def discounted_lifetime_service(annual_service: float, lifespan: float, discount_rate: float) -> float:
    """
    PV of constant annual service over lifespan with discount rate.
    """
    r = float(discount_rate)
    T = float(lifespan)
    return float(annual_service) * (1 - (1 + r) ** (-T)) / r


def average_over_years(s: pd.Series, start: int, end: int) -> float:
    years = list(range(int(start), int(end) + 1))
    return float(s.loc[years].mean())


def pick_peak_value(s: pd.Series) -> Tuple[int, float]:
    s2 = s.dropna()
    y = int(s2.idxmax())
    return y, float(s2.loc[y])


def xy(d: dict) -> tuple[list, list]:
    """Convenience for plotting: returns sorted x,y from dict."""
    return zip(*sorted(d.items())) if d else ([], [])


# =============================================================================
# Unit conversions
# =============================================================================

def twh_to_ej(twh: float) -> float:
    """Convert Terawatt-hours (TWh) to Exajoules (EJ)."""
    return float(twh) * 0.0036


def twh_to_ej_str(twh: float, decimals: int = 3) -> str:
    return f"{twh_to_ej(twh):.{int(decimals)}f}"


def gw_to_twh(gw: float, cap_factor: float) -> float:
    """Convert GW capacity to annual TWh given capacity factor."""
    return float(gw) * 8.760 * float(cap_factor)


# =============================================================================
# Deflator / FX helpers (no data loading here; pass Series in)
# =============================================================================

def gcam_deflator(value: float, *, arrDef: pd.Series, from_year: int, to_year: int) -> float:
    """
    Convert value in 'from_year dollars' to 'to_year dollars' using deflator index.
    """
    return float(value) * float(arrDef.loc[to_year]) / float(arrDef.loc[from_year])


def krw_per_usd_to_usd_per_krw(year: int, *, dfExcAnnual: pd.Series) -> float:
    """
    If dfExcAnnual[year] is KRW per USD, return USD per KRW for that year.
    """
    return 1.0 / float(dfExcAnnual.loc[int(year)])


def convert_base_usd(value: float, *, arrDef: pd.Series, from_base: int, to_base: int) -> float:
    """USD(to_base) = USD(from_base) * DEF[to_base] / DEF[from_base]."""
    return float(value) * float(arrDef.loc[to_base]) / float(arrDef.loc[from_base])


def series_convert_base(s: pd.Series, *, arrDef: pd.Series, from_base: int, to_base: int) -> pd.Series:
    """Convert a Series in USD(from_base) to USD(to_base)."""
    factor = float(arrDef.loc[to_base]) / float(arrDef.loc[from_base])
    return s * factor


# =============================================================================
# IO helpers
# =============================================================================

def write_text(path: str | Path, text: str) -> None:
    path = Path(path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


# =============================================================================
# Subsidy conversion
# =============================================================================

def subsidy_to_constant_usd_by_year(
    df: pd.DataFrame,
    *,
    dfExcAnnual: pd.Series,   # KRW per USD indexed by year
    arrDef: pd.Series,        # deflator index indexed by year
    base_year: int,
    year_col: str = "연도",
    val_col: str = "보조금 (만원)",
) -> pd.Series:
    """
    Convert subsidy series to constant USD(base_year) per vehicle, indexed by year.

    Assumptions:
      - val_col is in 만원 (10,000 KRW)
      - dfExcAnnual[year] = KRW per USD
      - arrDef[year] = deflator index
    """
    tmp = df.copy()
    tmp[year_col] = tmp[year_col].astype(int)
    tmp[val_col] = pd.to_numeric(tmp[val_col], errors="coerce")

    s_10kkrw = tmp.groupby(year_col)[val_col].mean()    # 만원
    s_krw = s_10kkrw * 10_000                           # KRW

    years = s_krw.index.astype(int)
    fx = dfExcAnnual.loc[years].astype(float)           # KRW/USD
    defl = arrDef.loc[years].astype(float)
    defl_base = float(arrDef.loc[int(base_year)])

    # nominal USD -> constant USD(base_year)
    return (s_krw / fx) * (defl_base / defl)


def df_scale(df: pd.DataFrame, col: str, scale: float, op: str) -> pd.DataFrame:
    """
    op='/' : divide by scale
    op='*' : multiply by scale
    """
    out = df.copy()
    if op == "/":
        out[col] = out[col] / float(scale)
    elif op == "*":
        out[col] = out[col] * float(scale)
    else:
        raise ValueError("op must be '/' or '*'")
    return out


# =============================================================================
# GCAM XML builders (string-based, reusable)
# =============================================================================

def build_ghgpolicy_fixedTax_xml(
    values_by_year: dict[int, float],
    *,
    policy_name: str,
    region_name: str = "South Korea",
    market_name: Optional[str] = "South Korea",
) -> str:
    if market_name is None:
        market_name = region_name

    lines = [
        '<?xml version="1.0" ?>',
        '<scenario>',
        '  <world>',
        f'    <region name="{region_name}">',
        f'      <ghgpolicy name="{policy_name}">',
        f'        <market>{market_name}</market>',
    ]

    for year in sorted(values_by_year):
        lines.append(f'        <fixedTax year="{year}">{values_by_year[year]:.1f}</fixedTax>')

    lines += [
        '      </ghgpolicy>',
        '    </region>',
        '  </world>',
        '</scenario>',
    ]
    return "\n".join(lines) + "\n"


def build_const_value_xml(
    values_by_year: dict[int, float],
    *,
    policy_name: str,
    region_name: str = "South Korea",
    policy_type: str = "tax",
    market_name: Optional[str] = None,
    min_price: bool = False,
    min_price_values_by_year: Optional[dict[int, float]] = None,
) -> str:
    if market_name is None:
        market_name = region_name

    if min_price and min_price_values_by_year is None:
        raise ValueError("min_price=True requires min_price_values_by_year (dict {year: value})")

    lines = [
        '<?xml version="1.0" ?>',
        '<scenario>',
        '  <world>',
        f'    <region name="{region_name}">',
        f'      <policy-portfolio-standard name="{policy_name}">',
        f'        <policyType>{policy_type}</policyType>',
        f'        <market>{market_name}</market>',
    ]

    if min_price:
        for year in sorted(min_price_values_by_year):
            lines.append(f'        <min-price year="{year}">{min_price_values_by_year[year]}</min-price>')

    for year in sorted(values_by_year):
        lines.append(f'        <constraint year="{year}">{values_by_year[year]}</constraint>')

    lines += [
        '      </policy-portfolio-standard>',
        '    </region>',
        '  </world>',
        '</scenario>',
    ]
    return "\n".join(lines) + "\n"


def build_const_techs_xml(
    years: Iterable[int],
    *,
    sector_name: str,
    subsector_name: str,
    policy_name: str,
    tech_names: Iterable[str],
    policy_type: str = "tax",
    region_name: str = "South Korea",
) -> str:
    years = list(years)

    def block(tech: str) -> list[str]:
        lines = [f'          <stub-technology name="{tech}">']
        for y in years:
            lines += [
                f'            <period year="{int(y)}">',
                f'              <input-{policy_type} name="{policy_name}"/>',
                '            </period>',
            ]
        lines.append('          </stub-technology>')
        return lines

    lines = [
        '<?xml version="1.0" ?>',
        '<scenario>',
        '  <world>',
        f'    <region name="{region_name}">',
        f'      <supplysector name="{sector_name}">',
        f'        <subsector name="{subsector_name}">',
    ]

    for tech in tech_names:
        lines += block(str(tech))

    lines += [
        '        </subsector>',
        '      </supplysector>',
        '    </region>',
        '  </world>',
        '</scenario>',
    ]
    return "\n".join(lines) + "\n"


def build_fixed_output_xml(
    values_by_year: dict[int, float],
    *,
    sector_name: str,
    subsector_name: str,
    tech_name: str,
    region_name: str = "South Korea",
) -> str:
    lines = [
        '<?xml version="1.0" ?>',
        '<scenario>',
        '  <world>',
        f'    <region name="{region_name}">',
        f'      <supplysector name="{sector_name}">',
        f'        <subsector name="{subsector_name}">',
        f'          <stub-technology name="{tech_name}">',
    ]

    for year in sorted(values_by_year):
        lines += [
            f'            <period year="{int(year)}">',
            f'              <fixedOutput>{values_by_year[year]}</fixedOutput>',
            '            </period>',
        ]

    lines += [
        '          </stub-technology>',
        '        </subsector>',
        '      </supplysector>',
        '    </region>',
        '  </world>',
        '</scenario>',
    ]
    return "\n".join(lines) + "\n"


def build_storage_techs_xml(
    blocks: list[dict],
    *,
    region_name: str = "South Korea",
    sector_name: str = "electricity",
    policy_name: str = "Other-Floor",
    policy_type: str = "subsidy",
) -> str:
    lines = [
        '<?xml version="1.0" ?>',
        '<scenario>',
        '  <world>',
        f'    <region name="{region_name}">',
        f'      <supplysector name="{sector_name}">',
    ]

    for blk in blocks:
        subsector = blk["subsector"]
        tech = blk["tech"]
        years = blk["years"]

        lines += [
            f'        <subsector name="{subsector}">',
            f'          <stub-technology name="{tech}">',
        ]

        for y in years:
            lines += [
                f'            <period year="{int(y)}">',
                f'              <input-{policy_type} name="{policy_name}"/>',
                '            </period>',
            ]

        lines += [
            '          </stub-technology>',
            '        </subsector>',
        ]

    lines += [
        '      </supplysector>',
        '    </region>',
        '  </world>',
        '</scenario>',
    ]
    return "\n".join(lines) + "\n"


# =============================================================================
# GCAM XML writer (ElementTree-based, reusable)
# =============================================================================

def records_to_gcam_xml(
    records: List[Dict],
    out_path: str,
    *,
    region_name: str = "South Korea",
) -> str:
    """
    Write records to GCAM stub-tech XML using <minicam-non-energy-input><input-cost>.
    Expected record keys:
      supplysector, subsector, tech, year, input_name, input_cost
    """
    scenario = ET.Element("scenario")
    world = ET.SubElement(scenario, "world")
    region = ET.SubElement(world, "region", {"name": region_name})

    ss_map, sub_map, tech_map, per_map = {}, {}, {}, {}

    def get_supplysector(name):
        if name not in ss_map:
            ss_map[name] = ET.SubElement(region, "supplysector", {"name": name})
        return ss_map[name]

    def get_subsector(ss_elem, name):
        key = (id(ss_elem), name)
        if key not in sub_map:
            sub_map[key] = ET.SubElement(ss_elem, "subsector", {"name": name})
        return sub_map[key]

    def get_stubtech(sub_elem, tech_name):
        key = (id(sub_elem), tech_name)
        if key not in tech_map:
            tech_map[key] = ET.SubElement(sub_elem, "stub-technology", {"name": tech_name})
        return tech_map[key]

    def get_period(tech_elem, year):
        key = (id(tech_elem), int(year))
        if key not in per_map:
            per_map[key] = ET.SubElement(tech_elem, "period", {"year": str(int(year))})
        return per_map[key]

    for r in records:
        ss = get_supplysector(r["supplysector"])
        sub = get_subsector(ss, r["subsector"])
        tech = get_stubtech(sub, r["tech"])
        per = get_period(tech, r["year"])

        mnei = ET.SubElement(per, "minicam-non-energy-input", {"name": r["input_name"]})
        ic = ET.SubElement(mnei, "input-cost")
        ic.text = f"{float(r['input_cost']):.4f}"

    xml_str = ET.tostring(scenario, encoding="utf-8")
    pretty = minidom.parseString(xml_str).toprettyxml(indent="  ", encoding="utf-8")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(pretty)

    return out_path


# =============================================================================
# PV factor (annuity)
# =============================================================================
def pv_factor(L: int, r: float) -> float:
    """Present-value factor for constant annual flow over L years at discount rate r."""
    L = int(L)
    r = float(r)
    return (1 - (1 + r) ** (-L)) / r


# =============================================================================
# Currency conversion helpers (KRW -> constant USD(base))
# =============================================================================
def krw_series_to_usd_base(
    s_krw: pd.Series,
    *,
    base_year: int,
    dfExcAnnual: pd.Series,  # KRW per USD
    arrDef: pd.Series,       # deflator index
) -> pd.Series:
    """
    Convert a per-year KRW series (indexed by year) to constant USD(base_year).
    USD_const(base) = (KRW / fx_year) * (DEF_base / DEF_year)
    """
    s_krw = s_krw.astype(float)
    years = s_krw.index.astype(int)

    fx = dfExcAnnual.loc[years].astype(float)          # KRW/USD
    defl = arrDef.loc[years].astype(float)
    defl_base = float(arrDef.loc[int(base_year)])

    return (s_krw / fx) * (defl_base / defl)


def krw_value_to_usd_base(
    value_krw: float,
    *,
    year: int,
    base_year: int,
    dfExcAnnual: pd.Series,
    arrDef: pd.Series,
) -> float:
    """Convert a single KRW value in 'year' to constant USD(base_year)."""
    y = int(year)
    fx = float(dfExcAnnual.loc[y])
    defl = float(arrDef.loc[y])
    defl_base = float(arrDef.loc[int(base_year)])
    return (float(value_krw) / fx) * (defl_base / defl)


def tenkkrw_series_to_usd_base(
    s_10kkrw: pd.Series,
    *,
    base_year: int,
    dfExcAnnual: pd.Series,
    arrDef: pd.Series,
) -> pd.Series:
    """Convert '만원'(10,000 KRW) series to constant USD(base_year)."""
    return krw_series_to_usd_base(
        s_10kkrw.astype(float) * 10_000,
        base_year=base_year,
        dfExcAnnual=dfExcAnnual,
        arrDef=arrDef,
    )


def baekmanwon_to_usd_base(
    value_baekmanwon: float,
    *,
    year: int,
    base_year: int,
    dfExcAnnual: pd.Series,
    arrDef: pd.Series,
) -> float:
    """Convert '백만원'(1,000,000 KRW) to constant USD(base_year)."""
    return krw_value_to_usd_base(
        float(value_baekmanwon) * 1_000_000,
        year=year,
        base_year=base_year,
        dfExcAnnual=dfExcAnnual,
        arrDef=arrDef,
    )


# =============================================================================
# Weighted-average helpers
# =============================================================================
def weighted_average(df: pd.DataFrame, value_col: str, weight_col: str) -> float:
    v = pd.to_numeric(df[value_col], errors="coerce")
    w = pd.to_numeric(df[weight_col], errors="coerce")
    mask = v.notna() & w.notna() & (w > 0)
    v = v[mask]
    w = w[mask]
    if w.sum() == 0:
        return float("nan")
    return float((v * w).sum() / w.sum())


def yearly_weighted_average(
    df: pd.DataFrame,
    *,
    year_col: str,
    value_col: str,
    weight_col: str,
) -> pd.DataFrame:
    """
    Return year-level table with weighted average.
    Output: year, total_weight, wavg_value
    """
    out = []
    for y, g in df.groupby(year_col):
        out.append({
            "year": int(y),
            "total_weight": float(pd.to_numeric(g[weight_col], errors="coerce").fillna(0).sum()),
            "wavg_value": weighted_average(g, value_col, weight_col),
        })
    return pd.DataFrame(out).sort_values("year").reset_index(drop=True)


# =============================================================================
# XML item helpers (de-dup + expansion)
# =============================================================================
def items_from_perf_df(df_bev_perf: pd.DataFrame, df_fcev_perf: pd.DataFrame, *, subsidy_name: str) -> list[dict]:
    """
    Build items list for XML using model-base perf subsidies:
      - Car/Bus: USD per pass-km
      - Truck:   USD per ton-km
    Requires index: ["Car", "Bus", "Medium truck"] and column "subsidy_per_perf".
    """
    bev_car = float(df_bev_perf.loc["Car", "subsidy_per_perf"])
    bev_bus = float(df_bev_perf.loc["Bus", "subsidy_per_perf"])
    bev_trk = float(df_bev_perf.loc["Medium truck", "subsidy_per_perf"])

    fcev_car = float(df_fcev_perf.loc["Car", "subsidy_per_perf"])
    fcev_bus = float(df_fcev_perf.loc["Bus", "subsidy_per_perf"])
    fcev_trk = float(df_fcev_perf.loc["Medium truck", "subsidy_per_perf"])

    return [
        dict(supplysector="trn_freight_road", subsector="Medium truck", tech="BEV",
             subsidy_name=subsidy_name, subsidy_value=bev_trk),
        dict(supplysector="trn_freight_road", subsector="Medium truck", tech="FCEV",
             subsidy_name=subsidy_name, subsidy_value=fcev_trk),

        dict(supplysector="trn_pass_road_LDV_4W", subsector="Car", tech="BEV",
             subsidy_name=subsidy_name, subsidy_value=bev_car),
        dict(supplysector="trn_pass_road_LDV_4W", subsector="Car", tech="FCEV",
             subsidy_name=subsidy_name, subsidy_value=fcev_car),

        # duplicate mapping for "Large Car and Truck"
        dict(supplysector="trn_pass_road_LDV_4W", subsector="Large Car and Truck", tech="BEV",
             subsidy_name=subsidy_name, subsidy_value=bev_car),
        dict(supplysector="trn_pass_road_LDV_4W", subsector="Large Car and Truck", tech="FCEV",
             subsidy_name=subsidy_name, subsidy_value=fcev_car),

        dict(supplysector="trn_pass_road", subsector="Bus", tech="BEV",
             subsidy_name=subsidy_name, subsidy_value=bev_bus),
        dict(supplysector="trn_pass_road", subsector="Bus", tech="FCEV",
             subsidy_name=subsidy_name, subsidy_value=fcev_bus),
    ]


def merge_items_sum(items: list[dict]) -> list[dict]:
    """Merge items with same (supplysector, subsector, tech, subsidy_name) by summing subsidy_value."""
    acc = {}
    for it in items:
        k = (it["supplysector"], it["subsector"], it["tech"], it["subsidy_name"])
        if k not in acc:
            acc[k] = dict(it)
            acc[k]["subsidy_value"] = float(it["subsidy_value"])
        else:
            acc[k]["subsidy_value"] += float(it["subsidy_value"])
    return list(acc.values())


def make_record(
    supplysector: str,
    subsector: str,
    tech: str,
    year: int,
    subsidy_name: str,
    subsidy_value: float,
    *,
    negative: bool = True,
) -> dict:
    v = -float(subsidy_value) if negative else float(subsidy_value)
    return dict(
        supplysector=supplysector,
        subsector=subsector,
        tech=tech,
        year=int(year),
        input_name=subsidy_name,
        input_cost=v,
    )


def make_records(items: list[dict], years: list[int], *, negative: bool = True) -> list[dict]:
    out = []
    for y in years:
        for it in items:
            out.append(make_record(
                supplysector=it["supplysector"],
                subsector=it["subsector"],
                tech=it["tech"],
                year=int(y),
                subsidy_name=it["subsidy_name"],
                subsidy_value=it["subsidy_value"],
                negative=negative,
            ))
    return out

def records_to_gcam_trn_fixed_output_xml(
    records: list[dict],
    out_path: str,
    *,
    region_name: str = "South Korea",
    subsector_tag: str = "tranSubsector",   # transport XML uses tranSubsector
) -> str:
    """
    Write transport fixedOutput records to GCAM XML.

    Each record must have:
      - supplysector: str
      - subsector: str               (will be written as <tranSubsector name="..."> by default)
      - tech: str                    (written as <stub-technology name="...">)
      - year: int
      - fixedOutput: float

    Produces:
      <supplysector>
        <tranSubsector>
          <stub-technology>
            <period year="YYYY"><fixedOutput>...</fixedOutput></period>
    """
    scenario = ET.Element("scenario")
    world = ET.SubElement(scenario, "world")
    region = ET.SubElement(world, "region", {"name": region_name})

    ss_map, sub_map, tech_map, per_map = {}, {}, {}, {}

    def get_supplysector(name: str):
        if name not in ss_map:
            ss_map[name] = ET.SubElement(region, "supplysector", {"name": name})
        return ss_map[name]

    def get_subsector(ss_elem, name: str):
        key = (id(ss_elem), name)
        if key not in sub_map:
            sub_map[key] = ET.SubElement(ss_elem, subsector_tag, {"name": name})
        return sub_map[key]

    def get_stubtech(sub_elem, tech_name: str):
        key = (id(sub_elem), tech_name)
        if key not in tech_map:
            tech_map[key] = ET.SubElement(sub_elem, "stub-technology", {"name": tech_name})
        return tech_map[key]

    def get_period(tech_elem, year: int):
        key = (id(tech_elem), int(year))
        if key not in per_map:
            per_map[key] = ET.SubElement(tech_elem, "period", {"year": str(int(year))})
        return per_map[key]

    for r in records:
        ss = get_supplysector(r["supplysector"])
        sub = get_subsector(ss, r["subsector"])
        tech = get_stubtech(sub, r["tech"])
        per = get_period(tech, int(r["year"]))

        fo = ET.SubElement(per, "fixedOutput")
        fo.text = f"{float(r['fixedOutput']):.2f}"

    xml_str = ET.tostring(scenario, encoding="utf-8")
    pretty = minidom.parseString(xml_str).toprettyxml(indent="  ", encoding="utf-8")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(pretty)

    return out_path