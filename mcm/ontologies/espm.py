# If the mapping is None, then there is no sensable mapping possible.

# TODO what if there are multiple options?
# TODO how do we deal with details that hint at another value:
#   Example: 'Courthouse - Number of Workers on Main Shift', maps directly to 'CommercialFacility: Number Of Occupants',
#   but, it also implies that the FacilityType is 'CommercialFacility: Primary Facility Type: Public Safety - Courthouse'

# Now, how do deal with multiple enum values that go into the same column?
#   Need to go into multiple rows for BEDES.
fields = 'fields'
types = 'types'

ONTOLOGY = {
    fields: {
        'Address 1': [
            'Site: Address Field 1',
            'CommercialFacility: Address Field 1',
            'ResidentialFacility: Address Field 1'
        ],
        'Address 2': [
            'Site: Address Field 2',
            'CommercialFacility: Address Field 2',
            'ResidentialFacility: Address Field 2'
        ],
        'City': 'Site: City',
        'Country': 'Site: Country',
        'County': 'Site: County',
        'Custom Property ID 1 - ID': 'Site: City ID Code', # TODO I *think* this is accurate.

        'Data Center - Cooling Equipment Redundancy': 'Cooling: Cooling Equipment Redundancy',
        'Data Center - Gross Floor Area (ft\\xef\\xbe\\xb2)': [
            'CommercialFacility: Gross Floor Area',
            'ActivityArea: Gross Floor Area'
        ],
        'Data Center - IT Energy Configuration': {
            'enum': 'EnergyUse: Energy Use Metric Type: Data Center - IT Energy Configuration',
            'value': 'EnergyUse: Complete Fuel', #?
        },
        'Data Center - IT Site Energy (kWh)': {
            'enum': 'EnergyUse: Energy Use Metric Type: Current Site IT Equipment Input Energy (kWh)',
            'value': 'EnergyUse: Complete Fuel' # ?
        },
        'Data Center - PDU Input Site Energy (kWh)': {
            'enum': 'EnergyUse: Energy Use Metric Type: Current Site PDU Input Energy (kWh)',
            'value': 'EnergyUse: Fuel' # ?
        },
        'Data Center - UPS Output Site Energy (kWh)': {
            'enum': 'EnergyUse: Energy Use Metric Type: Current Site UPS Output Energy (kWh)',
            'value': 'EnergyUse: Fuel' # ?
        },
        'Data Center - UPS System Redundancy': 'ITSystem: UPS System Redundancy',
        'Date Property Last Modified': [
            'CommercialFacility: PM Last Modified Date',
            'ResidentialFacility: PM Last Modified Date'
        ],
        'Direct GHG Emissions (MtCO2e)': {
            'enum': 'EnergyUse: Energy Use Metric Type: Current Direct GHG Emissions (MtCO2e)',
            'value': 'EnergyUse: Emissions Factor' #?
        },



        'Property Id': [
            'CommercialFacility: Federal Real Property ID',
            'RedidentalFacility: Federal Real Property ID'
        ],
        'Property Name': [
            'CommercialFacility: Name',
            'ResidentalFacility: Name',
        ],
        'Parent Property Id': None,
        'Parent Property Name': None,
        'Year Ending': 'EnergyUse: Energy Use Metric Type: Current Water Period Ending Date',
        'ENERGY STAR Score': 'EnergyUse: Energy Use Metric Type: Portfolio Manager Energy Performance Rating',
        
        "Property's Portfolio Manager Account Holder": None, # TODO: could be owner, opperator, who knows.
        'Electric Distribution Utility': 'EnergyUse: Utility',
    }
 }

common_building_types = [
    'Bank Branch',
    'Courthouse',
    'Hotel',
    'K-12 School',
    'Medical Office',
    'Office',
    'Retail Store',
    'Senior Care Community',
    'Supermarket/Grocery',
    'Non-Refrigerated Warehouse',
]

# There are some retitive fields whose values only change slightly.
for name in common_building_types:
    ONTOLOGY[fields]['{0} - Computer Density (Number per 1,000 ft\\xef\\xbe\\xb2)'.format(name)] =  'ITSystem:Density'
    ONTOLOGY[fields]['{0} - Gross Floor Area (ft\\xef\\xbe\\xb2)'.format(name)] = 'ITSystem: Density'
    ONTOLOGY[fields]['{0} - Number of Computers'.format(name)] = 'ITSystem: Quantity',
    ONTOLOGY[fields]['{0} - Number of Workers on Main Shift'.format(name)] = 'CommercialFacility: Number Of Occupants',
    ONTOLOGY[fields]['{0} - Percent That Can Be Cooled'.format(name)] = 'Cooling: Percent Of Floor Area Served'
    ONTOLOGY[fields]['{0} - Percent That Can Be Heated'.format(name)] = 'Heating: Percent Of Floor Area Served'
    ONTOLOGY[fields]['{0} - Weekly Operating Hours'.format(name)] = 'ActivityArea: Average Weekly Operating Hours',
    ONTOLOGY[fields]['{0} - Worker Density'.format(name)] = None


# For validation we need to know the type to coerce our string data 
# into, as well as which units are applicable.
# Our format is as follows:
#   'field key': ('type', 'units')
# If a field key is missing, it's presumed to be just ('str', None).
# I.e. non-measured observational or identification data.
ONTOLOGY[types] = {
        'EnergyUse: Energy Use Metric Type: Current Site PDU Input Energy (kWh)': ('float', 'kWh'),
}


