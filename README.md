# High Ambition Korea 2035 – A Replication Package

This repository provides the scenario configurations and policy input files accompanying:

> Choi, H., Park, S. & McJeon, H. High-ambition climate action in all sectors can achieve a 59% greenhouse gas emissions reduction in Korea by 2035. *Sci Rep* (2026). https://doi.org/10.1038/s41598-026-44130-2

**EarthArxiv preprint**: https://eartharxiv.org/repository/view/9937/

## Contact
- **Hyuntae Choi** – [hyuntae.choi.iam@gmail.com](mailto:hyuntae.choi.iam@gmail.com)  
- **Haewon McJeon** – [hmcjeon@kaist.ac.kr](mailto:hmcjeon@kaist.ac.kr)  
- **Sangin Park** – [sanpark@snu.ac.kr](mailto:sanpark@snu.ac.kr)  

---

## Repository Structure

| Directory / File | Description |
|------------------|-------------|
| `exe/` | Scenario configuration files for GCAM model runs |
| ├─ `configuration_Current_Policies_2035_Med.xml` | Main configuration for the *Current Policies* scenario under medium-range emissions assumptions |
| ├─ `configuration_High_Ambition_2035_Med.xml` | Main configuration for the *High Ambition* scenario under medium-range emissions assumptions |
| ├─ `configuration_Current_Policies_2035_Low.xml` | Sensitivity configuration for the *Current Policies* scenario under low-emissions assumptions |
| ├─ `configuration_High_Ambition_2035_Low.xml` | Sensitivity configuration for the *High Ambition* scenario under low-emissions assumptions |
| ├─ `configuration_Current_Policies_2035_High.xml` | Sensitivity configuration for the *Current Policies* scenario under high-emissions assumptions |
| ├─ `configuration_High_Ambition_2035_High.xml` | Sensitivity configuration for the *High Ambition* scenario under high-emissions assumptions |
| ├─ `configuration_High_Ambition_2035_Med_CPO2040.xml` | *High Ambition* scenario with coal phase-out extended to 2040 under medium-range emissions assumptions |
| ├─ `configuration_High_Ambition_2035_Med_AI.xml` | *High Ambition* scenario with AI-driven electricity demand increase under medium-range emissions assumptions |
| ├─ `configuration_Current_Policies_2035_Med_AI.xml` | *Current Policies* scenario with AI-driven electricity demand increase under medium-range emissions assumptions |
| `input/gcamdata/xml/` | GCAM XML input files (base and Korea-specific) |
| `input/policy/korea-2035/` | Sectoral policy input files for Korea’s 2035 mitigation scenarios |
| `input/solution/` | Solver configuration files |
| ├─ `cal_broyden_config.xml` | Broyden solver configuration for *Current Policies* scenarios |
| ├─ `cal_broyden_config_ep.xml` | Broyden solver configuration for *High Ambition* scenarios |

---

## Prerequisites

- **[GCAM v7.1](https://github.com/JGCRI/gcam-core/releases)** – Base model for GCAM-ROK

---

## Installation & Usage

### 1. Install GCAM v7.1

Download [GCAM v7.1](https://github.com/JGCRI/gcam-core/releases) and install it in a directory separate from this repository.  
Reference installation guides:  
- [Windows](https://www.youtube.com/watch?v=2Tv-5rryhk8)
- [MacOS](https://www.youtube.com/watch?v=AQnm_qZmypA) 
- [GCAM Build Instructions for Linux](https://jgcri.github.io/gcam-doc/gcam-build.html)

---

### 2. Attach Policy Input Files

- Copy the `./input/policy/korea-2035/` folder into the `input` folder of your GCAM installation.
- The required GCAM XML input files are already included in `input/gcamdata/xml/`.

### 3. Run Scenarios

Navigate to the `exe` directory in your GCAM v7.1 installation.

```bash
cd gcam-core/exe
```

Example (Windows PowerShell):

```powershell
.\gcam.exe -C configuration_Current_Policies_2035_Med.xml
.\gcam.exe -C configuration_High_Ambition_2035_Med.xml
```

Example (Linux/Mac):
```bash
./gcam -C configuration_Current_Policies_2035_Med.xml
./gcam -C configuration_High_Ambition_2035_Med.xml
```

## Citation
If you use this package in your work, please cite:
```text
Choi, H., Park, S. & McJeon, H. High-ambition climate action in all sectors can achieve
a 59% greenhouse gas emissions reduction in Korea by 2035. Sci Rep (2026).
https://doi.org/10.1038/s41598-026-44130-2
```

## License
[MIT License](https://opensource.org/licenses/MIT) – You are free to use, modify, and distribute this code with attribution.