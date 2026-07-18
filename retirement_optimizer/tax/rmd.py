from __future__ import annotations


UNIFORM_LIFETIME_DIVISORS = {
    73: 26.5, 74: 25.5, 75: 24.6, 76: 23.7, 77: 22.9, 78: 22.0, 79: 21.1,
    80: 20.2, 81: 19.4, 82: 18.5, 83: 17.7, 84: 16.8, 85: 16.0, 86: 15.2,
    87: 14.4, 88: 13.7, 89: 12.9, 90: 12.2, 91: 11.5, 92: 10.8, 93: 10.1,
    94: 9.5, 95: 8.9,
}


def rmd_start_age(birth_year: int) -> int:
    return 75 if birth_year >= 1960 else 73


def calculate_rmd(age: int, birth_year: int, prior_year_traditional_balance: float) -> float:
    if age < rmd_start_age(birth_year):
        return 0.0
    divisor = UNIFORM_LIFETIME_DIVISORS.get(age, max(1.0, 8.9 - 0.5 * (age - 95)))
    return max(0.0, prior_year_traditional_balance / divisor)
