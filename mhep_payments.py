# coding=utf-8
import pandas as pd

df = pd.read_csv("agreed_outcomes.csv",",")

# define areas and outcomes
areas = ["Haringey","Staffordshire","Tower Hamlets","Barnet", "Camden","Enfield"]
outcomes = [
    "Engagements",
    "Job starts",
    "Job outcome 6-wk (<16 hrs)",
    "Job outcome 6-wk (>16 hrs)",
    "Job sustain 6-mth (<16h hrs)",
    "Job sustain 6-mth (>16h hrs)"
    ]

# create empty lists for outcomes and payments
outcome_achieved = {}
accrued_BLF_payment = {"Total": []}
accrued_SOF_payment = {"Total": []}
# Tower Hamlets
MHEP_to_WWT = {"Block": [],"Total": []}
TH_to_WWT = {"Block": [], "Total": []}
WWT_to_MHEP = {"Total": []}

for area in areas:
    outcome_achieved[area] = {}
    accrued_SOF_payment[area] = []
    accrued_BLF_payment[area] = []
    for outcome in outcomes:
        outcome_achieved[area][outcome] = []
        for i in range(30):
            outcome_achieved[area][outcome].append(0)
    for i in range(30):
        accrued_SOF_payment[area].append(0)
        accrued_BLF_payment[area].append(0)

for i in range(30):
    accrued_BLF_payment["Total"].append(0)
    accrued_SOF_payment["Total"].append(0)
    MHEP_to_WWT["Block"].append(0)
    TH_to_WWT["Block"].append(0)
    MHEP_to_WWT["Total"].append(0)
    TH_to_WWT["Total"].append(0)
    WWT_to_MHEP["Total"].append(0)

for outcome in outcomes:
    MHEP_to_WWT[outcome] = []
    TH_to_WWT[outcome] = []
    WWT_to_MHEP[outcome] = []
    for i in range(30):
        MHEP_to_WWT[outcome].append(0)
        TH_to_WWT[outcome].append(0)
        WWT_to_MHEP[outcome].append(0)

# Define tariffs
SOF_tariffs = {
    outcomes[0]: 90,
    outcomes[1]:0,
    outcomes[2]:1250,
    outcomes[3]:1500,
    outcomes[4]:1750,
    outcomes[5]: 3000}

BLF_tariffs_1 = {
    outcomes[0]: 90,
    outcomes[1]: 0,
    outcomes[2]: 700,
    outcomes[3]: 1350,
    outcomes[4]: 1400,
    outcomes[5]: 1650}

BLF_tariffs_2 = {
    outcomes[0]: 90,
    outcomes[1]: 0,
    outcomes[2]: 2600,
    outcomes[3]: 3600,
    outcomes[4]: 0,
    outcomes[5]: 0}

def import_outcomes():
    for area in areas:
        for i in range(4,30):
          # Gets outcomes from area and quarter
          quarter = str(i)
          # Records outcomes in outcome_achieved - note exception for Tower Hamlets
          if area == "Tower Hamlets":
              outcome_achieved[area]["Engagements"][i] = df.loc[df["Area_Outcome"] == area + "Engagements (validated)"][quarter].item()
          else: outcome_achieved[area]["Engagements"][i] = df.loc[df["Area_Outcome"] == area + outcomes[0]][quarter].item()
          for outcome in outcomes:
                  if outcome != "Engagements": outcome_achieved[area][outcome][i] = df.loc[(df["Area"] == area) & (df["Outcome"] == outcome)][quarter].item()
    return outcome_achieved

def calculate_BLF_SOF_payments():
    for area in areas:
        for i in range(4,30):
            if (area in ["Tower Hamlets","Staffordshire", "Haringey", "Barnet"]) and i < 13:
                for outcome in outcomes:
                    accrued_SOF_payment[area][i] += outcome_achieved[area][outcome][i] * SOF_tariffs[outcome]
            if (area in ["Tower Hamlets","Staffordshire"]) and i >= 13:
                for outcome in outcomes:
                    accrued_BLF_payment[area][i] += outcome_achieved[area][outcome][i] * BLF_tariffs_1[outcome]
            if (area in ["Camden","Haringey","Enfield"]) and i >= 13:
                for outcome in outcomes:
                    accrued_BLF_payment[area][i] += outcome_achieved[area][outcome][i] * BLF_tariffs_2[outcome]
            accrued_BLF_payment["Total"][i] += accrued_BLF_payment[area][i]
            accrued_SOF_payment["Total"][i] += accrued_SOF_payment[area][i]

def calculate_TH_payments(TH_outcomes):
    for i in range(5,7):
        MHEP_to_WWT["Block"][i] = 10237.50
        # Note: engagements validated != engagements paid for in year 1
        MHEP_to_WWT["Engagements"][i] = 136.50 * TH_outcomes["Engagements"][i]
    for i in range(7,10):
        MHEP_to_WWT["Engagements"][i] = 273 * TH_outcomes["Engagements"][i]
    for i in range(10,13):
        MHEP_to_WWT["Job starts"][i] = 822 * TH_outcomes["Job starts"][i]

    # Year 2018/19. Note MHEP payment cap of £90,300 for job start payments and CCG payment cap of £88,000 for first 50 job starts plus £210,670 in total
    MHEP_payment_cap_18_19 = 90300
    WWT_payment_cap_18_19 = 88000
    TH_jobstarts_cap_18_19 = 50 # after which payment goes down to £822 per job start
    MHEP_to_WWT_total_18_19 = 0
    WWT_to_MHEP_total_18_19 = 0
    total_18_19_job_starts = 0
    MHEP_cap_met = False
    WWT_cap_met = False
    TH_jobstarts_cap_met = False

    for i in range(13,17):
        MHEP_to_WWT["Block"][i] = 22000
        if MHEP_cap_met == False: MHEP_to_WWT["Job starts"][i] = 822 * TH_outcomes["Job starts"][i]
        if WWT_cap_met == False: WWT_to_MHEP["Job starts"][i] = 1760 * TH_outcomes["Job starts"][i]
        if TH_jobstarts_cap_met == False: TH_to_WWT["Job starts"][i] = 2582 * TH_outcomes["Job starts"][i]

        # Check MHEP payment cap
        if MHEP_to_WWT_total_18_19 + MHEP_to_WWT["Job starts"][i] > MHEP_payment_cap_18_19:
            MHEP_cap_met = True
            MHEP_to_WWT["Job starts"][i] = MHEP_payment_cap_18_19 - MHEP_to_WWT_total_18_19
        # Update running total
        MHEP_to_WWT_total_18_19 += MHEP_to_WWT["Job starts"][i]

        # Check WWT payment cap
        if WWT_to_MHEP_total_18_19 + WWT_to_MHEP["Job starts"][i] > WWT_payment_cap_18_19:
            WWT_cap_met = True
            WWT_to_MHEP["Job starts"][i] = WWT_payment_cap_18_19 - WWT_to_MHEP_total_18_19
        # Update running total
        WWT_to_MHEP_total_18_19 += WWT_to_MHEP["Job starts"][i]

        # Check TH job starts payment cap
        if total_18_19_job_starts + TH_outcomes["Job starts"][i] > TH_jobstarts_cap_18_19:
            TH_jobstarts_cap_met = True
            TH_to_WWT["Job starts"][i] = 2582 * (TH_jobstarts_cap_18_19 - total_18_19_job_starts) + 822 * (TH_outcomes["Job starts"][i] - (TH_jobstarts_cap_18_19 - total_18_19_job_starts))
        # Update running total
        total_18_19_job_starts += TH_outcomes["Job starts"][i]

    # Calculates total payments
    for i in range(30):
        MHEP_to_WWT["Total"][i] = 0
        WWT_to_MHEP["Total"][i] = 0
        TH_to_WWT["Total"][i] = 0
        for outcome in outcomes:
            MHEP_to_WWT["Total"][i] += MHEP_to_WWT[outcome][i]
            WWT_to_MHEP["Total"][i] += WWT_to_MHEP[outcome][i]
            TH_to_WWT["Total"][i] += TH_to_WWT[outcome][i]
        MHEP_to_WWT["Total"][i] += MHEP_to_WWT["Block"][i]
        if i == 3:
            TH_to_WWT["Annual payment"][i] = annual_payment[scenario]
            TH_to_WWT["Total"][i] += annual_payment[scenario]

#calculate_payments()
import_outcomes()
calculate_BLF_SOF_payments()

# Tower Hamlets payments
TH_outcomes = {}
for outcome in outcomes:
    TH_outcomes[outcome] = []
    for i in range(30):
        TH_outcomes[outcome].append(0)
        if outcome == "Engagements" and i >= 4 and i < 9: TH_outcomes[outcome][i] = df.loc[df["Area_Outcome"] == "Tower Hamlets" + "Engagements (that MHEP paid WWT for)"][str(i)].item()
        elif i >= 4: TH_outcomes[outcome][i] = outcome_achieved["Tower Hamlets"][outcome][i]

calculate_TH_payments(TH_outcomes)


all_payments = []
all_payments_df = pd.DataFrame(all_payments)
for area in areas:
    for a in 0,1:
      if a == 0: all_payments_df.rename(index={areas.index(area)*2+a: area + ": SOF payments"},inplace=True)
      if a == 1: all_payments_df.rename(index={areas.index(area)*2+a: area + ": BLF payments"},inplace=True)
# all_payments_df.sort_index(ascending=True)
all_payments_df.to_excel(pd.ExcelWriter("all_payments.xlsx"))
