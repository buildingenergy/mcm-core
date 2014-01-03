"""
This module describes how data is mapped from our ontology to Django Models.

The structure pulls out the read data from our espm-based MCM run, like follows:

espm['flat_schema'].keys() -> model.attr mapping

All fields found in the ontology, but not mentioned in this mapping
go into the ``extra_data`` attribute, which is a json field in Postgres.

"""
MAP = {
    # Could there be a better key for this?
    u'Property Id': u'property_id',
    u'Address 1': u'address_line_1',
    u'Address 2': u'address_line_2',
    u'City': u'city',
    u'County': u'county',
    u'Country': u'country',
    u'City': u'city',
    u'Postal Code': u'postal_code',
    # Not sure what to do about this, no `Organization` field exists.
    #u'Organization': '?'
    u'State/Province': u'state_province',
    u'Property Floor Area (Buildngs and Parking)': (
        u'property_floor_area_bldg_park'
    ),
    u'Property Floor Area (Building(s))': u'property_floor_area_bldg',
    u'Property Floor Area (Parking)': u'property_floor_area_park',
    u'Year Built': u'year_built',
    u'Year Ending': u'year_ending',
    u'Energy Alerts': u'energy_alerts',
    u'ENERGY STAR Score': u'energy_score',
    u'ENERGY STAR Certification - Year(s) Certified': u'energy_star_cert_years',
    u'National Median ENERGY STAR Score': u'national_median_energy_star_score',
    u'National Median Reference Property Type': u'national_median_ref_prop_type',
    u'National Median Site EUI': u'national_median_site_eui',
    u'National Median Source EUI': u'national_median_source_eui',
    u'National Median Source Energy Use': u'national_median_site_energy_use',
    u'Site EUI': u'site_eui',
    # Might we want `Site Energy Use` at some point?
    u'Source EUI': u'source_eui',
    u'Total GHG Emissions': u'total_ghg_emissions',
    u'Weather Normalized Site EUI': u'weather_normalized_site_eui',
    u'Weather Normalized Source EUI': u'weather_normalized_source_eui',
    u'Generation Date': u'generation_date',
    u'Release Date': u'release_date',
}
