from utils import discounted_lifetime_service

"""
Common parameters and helper functions for vehicle lifetime service calculations
(All values in real terms; discounting applied to annual service flows)
"""

# =============================
# Global constants
# =============================

DAYS_IN_YEAR = 365
DISCOUNT_RATE = 0.045  # 4.5% discount rate

# =============================
# Vehicle-specific parameters
# =============================

# --- Car (pass-km / veh) ---
CAR_DAILY_MILEAGE = 44.3          # km / veh / day
CAR_LIFESPAN = 15.3               # years
CAR_LOAD_FACTOR = 1.26            # passengers / veh

CAR_ANNUAL_SERVICE = (
    CAR_DAILY_MILEAGE * DAYS_IN_YEAR * CAR_LOAD_FACTOR
)

CAR_PASS_KM_PER_VEH_DISCOUNTED = discounted_lifetime_service(
    CAR_ANNUAL_SERVICE, CAR_LIFESPAN, DISCOUNT_RATE
)


# --- Bus (pass-km / veh) ---
BUS_DAILY_MILEAGE = 162.0         # km / veh / day
BUS_LIFESPAN = 15.5               # years
BUS_LOAD_FACTOR = 12.84           # passengers / veh

BUS_ANNUAL_SERVICE = (
    BUS_DAILY_MILEAGE * DAYS_IN_YEAR * BUS_LOAD_FACTOR
)

BUS_PASS_KM_PER_VEH_DISCOUNTED = discounted_lifetime_service(
    BUS_ANNUAL_SERVICE, BUS_LIFESPAN, DISCOUNT_RATE
)


# --- Medium Truck (ton-km / veh) ---
TRUCK_DAILY_MILEAGE = 50.7        # km / veh / day
TRUCK_LIFESPAN = 16.8             # years
TRUCK_LOAD_FACTOR = 4.2           # tonnes / veh

TRUCK_ANNUAL_SERVICE = (
    TRUCK_DAILY_MILEAGE * DAYS_IN_YEAR * TRUCK_LOAD_FACTOR
)

TRUCK_TON_KM_PER_VEH_DISCOUNTED = discounted_lifetime_service(
    TRUCK_ANNUAL_SERVICE, TRUCK_LIFESPAN, DISCOUNT_RATE
)


# =============================
# Sanity-check block (optional)
# =============================

if __name__ == "__main__":
    print("Discount rate:", DISCOUNT_RATE)
    print("Car discounted lifetime service (pass-km/veh):",
          CAR_PASS_KM_PER_VEH_DISCOUNTED)
    print("Bus discounted lifetime service (pass-km/veh):",
          BUS_PASS_KM_PER_VEH_DISCOUNTED)
    print("Medium truck discounted lifetime service (ton-km/veh):",
          TRUCK_TON_KM_PER_VEH_DISCOUNTED)