import csv
from collections import defaultdict

# Storing these files in the repo for now, would be better if they were stored some other way.
SLCSP_PATH = 'files/slcsp.csv'
ZIPS_PATH = 'files/zips.csv'
PLANS_PATH = 'files/plans.csv'


def get_target_zip_codes_and_states():
    """
    Creates a list of zipcodes from the slcsp.csv file and gets and
    returns a dict of the target zipcode and state key, value pairs from the zips.csv file.
    """
    with open(SLCSP_PATH, 'r') as slcsp_file:
        reader = csv.reader(slcsp_file, delimiter=',')
        next(reader, None)  # skip the headers (zipcode, rate)
        # create a set of all the target zipcodes that need rates
        target_zips_set = set([row.split(',')[0] for row in slcsp_file])

    # get all matching zip codes (and their respective states) from zips.csv
    matches = {}  # chose dict so there wouldn't be any duplicates
    with open(ZIPS_PATH, 'r') as zips_file:
        for line in zips_file:
            if line.split(',')[0] in target_zips_set:
                matches[line.split(',')[0]] = line.split(',')[1]
    return matches


def find_all_matching_silver_plan_rates(matching_zip_codes):
    """
    Creates a dict of plan rates per state. State is the key and
    the list of plan rates is the value.
    """
    with open(PLANS_PATH, 'r') as plans_file:
        reader = csv.reader(plans_file, delimiter=',')
        next(reader, None)  # skip the headers (plan_id, state, metal_level, rate, rate_area)
        plan_rates_per_state = defaultdict(list)
        for line in plans_file:
            state = line.split(',')[1]
            metal_level = line.split(',')[2]
            plan_rate = line.split(',')[3]
            if state in matching_zip_codes.values() and metal_level == 'Silver':
                plan_rates_per_state[state].append(plan_rate)  # TODO: Does not keep trailing zeroes, need another solution

        return plan_rates_per_state


def merge_plans_and_zipcodes(plan_rates_states, matching_zip_codes_states):
    """
    Merges the zipcodes, states dict with the plan rates per state dict. Returns a dict of zipcodes
    as the key and a list of the plan rates as the value.
    """
    zipcodes_and_rates = {k: plan_rates_states.get(v) for k, v in matching_zip_codes_states.items()}
    return zipcodes_and_rates


def get_final_slcsp_rates(zipcodes_and_rates):
    """
    Takes the zipcodes_and_rates dict and sorts the plan rates and sets
    the value as the second-lowest cost silver plan or as None (if there is 0 or 1 plan).
    Prints out the zipcode and rates in the same order as presented in
    slcsp.csv and creates an output file with the results in the /files directory.
    """
    for key, value in zipcodes_and_rates.items():
        if value and len(value) >= 2:
            value.sort()
            zipcodes_and_rates[key] = value[1]
        else:
            # if value is None or len(value) <= 2 -> value = None
            zipcodes_and_rates[key] = None
    print("zipcode,rate")
    with open(SLCSP_PATH, 'r') as slcsp_file:
        with open('files/output.csv', 'w') as output:
            # TODO: fix the csv output formatting, need to add spaces and commas
            writer = csv.writer(output)
            writer.writerow(['zipcode', 'rate'])
            reader = csv.reader(slcsp_file, delimiter=',')
            next(reader, None)  # skip the headers (zipcode, rate)
            for line in slcsp_file:
                zipcode = line.replace(',', '').strip('\n')
                second_lowest_silver_rate = zipcodes_and_rates[zipcode]
                if second_lowest_silver_rate is None:
                    # Do not print out a rate if the value is set to None
                    writer.writerow([zipcode])
                    print(f"{zipcode},")
                else:
                    writer.writerow([zipcode, second_lowest_silver_rate])
                    print(f"{zipcode}, {second_lowest_silver_rate}")


target_zip_codes = get_target_zip_codes_and_states()
silver_plan_rates = find_all_matching_silver_plan_rates(target_zip_codes)
zipcodes_and_silver_rates = merge_plans_and_zipcodes(silver_plan_rates, target_zip_codes)
get_final_slcsp_rates(zipcodes_and_silver_rates)
