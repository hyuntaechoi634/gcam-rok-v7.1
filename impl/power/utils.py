from pathlib import Path

def twh_to_ej(twh):
    """
    Convert Terawatt-hours (TWh) to Exajoules (EJ).

    Parameters:
    twh (float): Energy in Terawatt-hours.

    Returns:
    float: Energy in Exajoules.
    """
    conversion_factor = 0.0036
    return twh * conversion_factor

def xy(d):
    return zip(*sorted(d.items())) if d else ([], [])

def gw_to_twh(gw, cap_factor):
    return gw * 8.760 * cap_factor

def twh_to_ej_str(twh, decimals=3):
    return f"{twh_to_ej(twh):.{decimals}f}"

def write_text(path, text):
    path = Path(path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def build_const_value_xml(
    values_by_year,
    *,
    policy_name,
    region_name='South Korea',
    policy_type="tax",
    market_name=None,
    min_price=False,
    min_price_values_by_year=None,
):
    if market_name is None:
        market_name = region_name

    if min_price:
        if min_price_values_by_year is None:
            raise ValueError(
                "min_price=True requires min_price_values_by_year (dict {year: value})"
            )

    lines = [
        '<?xml version="1.0" ?>',
        '<scenario>',
        '  <world>',
        f'    <region name="{region_name}">',
        f'      <policy-portfolio-standard name="{policy_name}">',
        f'        <policyType>{policy_type}</policyType>',
        f'        <market>{market_name}</market>',
    ]

    # --- min-price block (optional) ---
    if min_price:
        for year in sorted(min_price_values_by_year):
            lines.append(
                f'        <min-price year="{year}">{min_price_values_by_year[year]}</min-price>'
            )

    # --- constraint block ---
    for year in sorted(values_by_year):
        lines.append(
            f'        <constraint year="{year}">{values_by_year[year]}</constraint>'
        )

    lines += [
        '      </policy-portfolio-standard>',
        '    </region>',
        '  </world>',
        '</scenario>',
    ]

    return '\n'.join(lines) + '\n'

def build_const_techs_xml(
    years,
    *,
    sector_name,
    subsector_name,
    policy_name,
    tech_names,
    policy_type='tax',
    region_name='South Korea',
):
    def block(tech):
        lines = [f'          <stub-technology name="{tech}">']
        for year in years:
            lines += [
                f'            <period year="{year}">',
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
        lines += block(tech)

    lines += [
        '        </subsector>',
        '      </supplysector>',
        '    </region>',
        '  </world>',
        '</scenario>',
    ]

    return '\n'.join(lines) + '\n'

def build_fixed_output_xml(
    values_by_year,
    *,
    sector_name,
    subsector_name,
    tech_name,
    region_name="South Korea",
):
    """
    Build GCAM XML with <fixedOutput> by period.

    values_by_year : dict {year: value}
        fixedOutput values (e.g., EJ)
    """

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
            f'            <period year="{year}">',
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

    return '\n'.join(lines) + '\n'

def build_storage_techs_xml(
    blocks,
    *,
    region_name="South Korea",
    sector_name="electricity",
    policy_name="Other-Floor",
    policy_type="subsidy",
):
    """
    blocks: list of dicts, e.g.
      [
        {
          "subsector": "solar",
          "tech": "PV_storage",
          "years": [2025, 2030, 2035],
        },
        {
          "subsector": "wind",
          "tech": "wind_storage",
          "years": [2025, 2030, 2035],
        },
      ]
    """

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
                f'            <period year="{y}">',
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

    return '\n'.join(lines) + '\n'
