# High Ambition Korea 2035 – A Replication Package

This repository provides the scenario configurations and policy input files accompanying:

> Choi, H., Park, S., & McJeon, H. *High-ambition climate action in all sectors can achieve a 58% greenhouse gas emissions reduction in Korea by 2035*. [Working Paper / Preprint link]

## Contact
- **Hyuntae Choi** – [chti0265@snu.ac.kr](mailto:chti0265@snu.ac.kr)  
- **Haewon McJeon** – [hmcjeon@kaist.ac.kr](mailto:hmcjeon@kaist.ac.kr)  
- **Sangin Park** – [sanpark@snu.ac.kr](mailto:sanpark@snu.ac.kr)  

---

## Repository Structure

| Directory / File | Description |
|------------------|-------------|
| `exe/` | Scenario configuration files for GCAM model runs |
| ├─ `configuration_Current_Policies_Med.xml` | Main configuration for the *Current Policies* scenario under medium-range emissions assumptions |
| ├─ `configuration_High_Ambition_Med.xml` | Main configuration for the *High Ambition* scenario under medium-range emissions assumptions |
| ├─ `configuration_Current_Policies_Low.xml` | Sensitivity configuration for the *Current Policies* scenario under low-emissions assumptions |
| ├─ `configuration_High_Ambition_Low.xml` | Sensitivity configuration for the *High Ambition* scenario under low-emissions assumptions |
| ├─ `configuration_Current_Policies_High.xml` | Sensitivity configuration for the *Current Policies* scenario under high-emissions assumptions |
| ├─ `configuration_High_Ambition_High.xml` | Sensitivity configuration for the *High Ambition* scenario under high-emissions assumptions |
| ├─ `configuration_High_Ambition_Med_CPO2040.xml` | *High Ambition* scenario with coal phase-out extended to 2040 under medium-range emissions assumptions |
| ├─ `configuration_High_Ambition_Med_AI.xml` | *High Ambition* scenario with AI-driven electricity demand increase under medium-range emissions assumptions |
| `input/policy/korea-2035/` | Sectoral policy input files for Korea’s 2035 mitigation scenarios |

---

## Prerequisites

- **[GCAM v7.1](https://github.com/JGCRI/gcam-core/releases)** – Base model for GCAM-ROK

---

## Installation & Usage

### 1. Install GCAM v7.1

Download [GCAM v7.1](https://github.com/JGCRI/gcam-core/releases) and install it in a directory separate from this repository.  
Reference installation guides:  
- [Windows](https://www.youtube.com/watch?v=2Tv-5rryhk8) – P. Patel  
- [MacOS](https://www.youtube.com/watch?v=AQnm_qZmypA) – P. Patel  
- [GCAM Build Instructions for Linux](https://jgcri.github.io/gcam-doc/gcam-build.html)

---

### 2. Attach Policy Input Files

- Copy the `./input/policy/korea-2035/` folder into the `input` folder of your GCAM installation.
- Download the required GCAM XML input files from the following folder:
  https://drive.google.com/drive/folders/1WRlMSj8AzUgIrtq0SrSJqcSE6OKhmm2C?usp=sharing

  This folder contains all base and Korea-specific XML inputs required to run the scenarios.
  Place all contents into:
  `input/gcamdata/xml/`

### 3. Run Scenarios

Navigate to the `exe` directory in your GCAM v7.1 installation.

Example (Windows PowerShell):

```powershell
.\gcam.exe -C configuration_Current_Policies_Med.xml
.\gcam.exe -C configuration_High_Ambition_Med.xml

```

Example (Linux/Mac):
```bash
./gcam -C configuration_Current_Policies_Med.xml
./gcam -C configuration_High_Ambition_Med.xml
```

## Citation
If you use this package in your work, please cite:
```text
Choi, H., Park, S., & McJeon, H. (2025).
High-ambition climate action in all sectors can achieve a 60% greenhouse gas emissions reduction in Korea by 2035. Working Paper.
[Preprint link or DOI]
```

## License
[MIT License](https://opensource.org/licenses/MIT) – You are free to use, modify, and distribute this code with attribution.