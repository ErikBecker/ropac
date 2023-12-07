# ROPAC - Radar Observations Processing and Compositing

## Installing ROPAC

Assuming that conda has already been installed

1. **Clone the Repository:**
    ```bash
    git clone https://github.com/ErikBecker/ropac.git
    cd ropac
    ```
2. **Setup conda environment:**
    ```bash 
    conda env create -f ropac_env.yml
    ```
3. **Install ROPAC:**
    ```bash
    source activate ropac
    python setup.py install 
    ```

    for developer use:
    ```bash
    python setup.py develop
    ```

    To uninstall:
    ```bash
    python setup.py develop --uninstall
    ```
## Setup ROPAC configuration

1. **Setup config files in your working directory:**
    ```bash
    cd /path/to/your/working/directory
    mkdir config
    cd config
    touch sysconfig.yaml
    ```

    The *sysconfig.yaml* should contain the following:

    Replace */path/to/your/data/directory* with your directory structure

    ```yaml
    directories:
        data: /path/to/your/data/directory
        logs: /path/to/your/data/directory/logs
        images: /path/to/your/data/directory/images

    logging-settings:
        # Select: DEBUG, INFO, WARNING, ERROR, or CRITICAL
        log_level: ERROR
        # Select: FILE, TERMINAL, BOTH, or NONE
        output_level: NONE
        # Select: DEBUG, INFO, WARNING, ERROR, or CRITICAL
        system_log_level: ERROR
        # Select: FILE, TERMINAL, BOTH, or NONE
        system_output_level: NONE
    ```

2. **Setup *CONFIG_PATH* to point to your config directory**
    
    Replace */path/to/your/working/directory/config* with your directory structure and make sure ropac env is active, then run:

    ```bash
    conda env config vars set CONFIG_PATH=/path/to/your/working/directory/config
    conda deactivate 
    conda activate ropac
    ```   

    Check if env loaded variable
    ```bash
    conda env config vars list
    env | grep CONFIG_PATH
    ```

    To remove run:
    ```bash
    conda env config vars unset YOUR_VARIABLE_NAME
    ```

3. **Setup radar config files**

    The *radars* directory need to be located in the config directory as below:
    ```bash
    config
    ├── radars
    │   ├── 0080.yaml
    │   └── Gematronik.yaml
    └── sysconfig.yaml
    ```
    
    They must follow a strict naming convention. See "radar".yaml inside demo directory for more info.


## Running ROPAC demo

1. **Active Env if not active**
    ```bash
    source activate ropac
    ```
2. **Install jupyter notebook if not already installed:**
    ```bash
    pip install notebook
    ```
3. **Launch notebook:**
    ```bash
    jupyter notebook demo/ropac_demo.ipynb 
    ```

