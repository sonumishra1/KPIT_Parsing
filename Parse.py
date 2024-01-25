import xml.etree.ElementTree as ET
import pandas as pd
import logging
from tkinter import filedialog, Tk

def rec_func(parent, prefix, logger):
    try:
        short_name = parent.find(f'.//{prefix}SHORT-NAME')
        def_ref = parent.find(f'.//{prefix}DEFINITION-REF')
        return short_name, def_ref
    except:
        logger.error('Error reading SHORT_NAME and/or DEFINITION_REF. Check XML')
        raise

def create_logger():
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    return logger

def run(xml_file='AutosarFile.xml'):
    logger = create_logger()

    root = Tk()
    root.withdraw()
    
    # GUI for selecting input and output files
    input_file = filedialog.askopenfilename(title="Select Autosar XML file", filetypes=[("XML files", "*.xml")])
    output_file = filedialog.asksaveasfilename(title="Save Excel report as", defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])

    try:
        # Add headers
        headers = ['Type', 'Parent', 'Short_Name', 'Definition_Ref']

        # Read XML
        data = parse_xml(input_file, logger)

        # Create pandas dataframe
        df = pd.DataFrame(data, columns=headers) 

        # Save to xlsx
        df.to_excel(output_file, index=False)
        logger.info('Data saved to file: {}'.format(output_file))
    except Exception as e:
        logger.error(f'Error: {str(e)}')

def parse_xml(xml_file, logger):
    logger.info('Reading XML file: {}'.format(xml_file))
    tree = ET.parse(xml_file)
    root = tree.getroot()
    prefix = root.tag.split('}')[0] + r'}'
    ar_packages = root.findall(f'.//{prefix}AR-PACKAGE')
    data = []
    for ar_package in ar_packages:
        elements = ar_package.find(f'.//{prefix}ELEMENTS')
        ecuc_mod_config_vals = elements.findall(f'.//{prefix}ECUC-MODULE-CONFIGURATION-VALUES')
        for ecuc_mod_config_val in ecuc_mod_config_vals:
            containers = ecuc_mod_config_val.findall(f'.//{prefix}CONTAINERS')
            for container in containers:
                container_short_name, container_def_ref = rec_func(container, prefix, logger)
                data.append(['CONTAINERS', container.tag.replace(prefix,''), container_short_name.text, container_def_ref.text])
                sub_containers = container.findall(f'.//{prefix}SUB-CONTAINERS')
                for sub_container in sub_containers:
                    ecuc_cont_vals = sub_container.findall(f'.//{prefix}ECUC-CONTAINER-VALUE')
                    for ecuc_cont_val in ecuc_cont_vals:
                        sub_cont_short_name, sub_cont_def_ref = rec_func(ecuc_cont_val, prefix, logger)
                        data.append(['SUB-CONTAINERS', ecuc_cont_val.tag.replace(prefix,''), sub_cont_short_name.text, sub_cont_def_ref.text])

    logger.info('XML file: {} read successfully'.format(xml_file))
    return data

if __name__ == "__main__":
    run()
