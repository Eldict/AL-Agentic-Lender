# Tests for calculations.py (the numbers the underwriter relies on).

import pytest

from al_ai import calculations as calc


# income normalisation

@pytest.mark.parametrize("amount, freq, expected", [
    (1000, "weekly", 52_000),
    (2000, "fortnightly", 52_000),
    (5000, "monthly", 60_000),
    (60000, "yearly", 60_000),
    (60000, "Annual", 60_000),          # case-insensitive
    (5000, " monthly ", 60_000),        # whitespace-tolerant
])
def test_normalise_to_yearly(amount, freq, expected):
    assert calc.normalise_to_yearly(amount, freq) == expected


def test_normalise_unknown_frequency_raises():
    with pytest.raises(ValueError):
        calc.normalise_to_yearly(100, "daily")


def test_normalise_negative_income_raises():
    with pytest.raises(ValueError):
        calc.normalise_to_yearly(-1, "monthly")


# repayment

@pytest.mark.parametrize("principal, rate, years, expected", [
    (300_000, 4.0, 30, 1432.25),
    (250_000, 3.5, 25, 1251.56),
    (200_000, 6.0, 30, 1199.10),
])
def test_monthly_repayment_known_values(principal, rate, years, expected):
    assert calc.monthly_repayment(principal, rate, years) == pytest.approx(expected, abs=0.01)


def test_monthly_repayment_zero_rate():
    assert calc.monthly_repayment(120_000, 0.0, 10) == pytest.approx(1000.0)


def test_monthly_repayment_zero_loan():
    assert calc.monthly_repayment(0, 4.0, 30) == 0


def test_monthly_repayment_invalid_term():
    with pytest.raises(ValueError):
        calc.monthly_repayment(100_000, 4.0, 0)


def test_max_principal_is_inverse_of_repayment():
    payment = calc.monthly_repayment(320_000, 4.5, 28)
    assert calc.max_principal_for_payment(payment, 4.5, 28) == pytest.approx(320_000, abs=0.01)


def test_stressed_rate_and_repayment_is_higher():
    rate = calc.stressed_rate(4.0, 2.0)
    assert rate == 6.0
    assert calc.monthly_repayment(300_000, rate, 30) > calc.monthly_repayment(300_000, 4.0, 30)


# ratios

def test_dti_includes_new_mortgage():
    # (400 debts + 1,600 mortgage) / 5,000 income = 40%
    assert calc.dti(400, 1600, 5000) == pytest.approx(0.40)


def test_dti_zero_income_raises():
    with pytest.raises(ValueError):
        calc.dti(100, 1000, 0)


def test_lti():
    assert calc.lti(240_000, 60_000) == pytest.approx(4.0)


def test_lti_zero_income_raises():
    with pytest.raises(ValueError):
        calc.lti(100_000, 0)


def test_ltv_uses_lower_of_price_and_estimate():
    # Asking 400k but estimated 360k: LTV is on 360k
    assert calc.ltv(324_000, 400_000, 360_000) == pytest.approx(0.90)
    # Estimate above asking: LTV is on the asking price
    assert calc.ltv(324_000, 360_000, 400_000) == pytest.approx(0.90)


def test_ltv_without_estimate_uses_asking_price():
    assert calc.ltv(270_000, 300_000) == pytest.approx(0.90)


def test_ltv_zero_value_raises():
    with pytest.raises(ValueError):
        calc.ltv(100_000, 0)


def test_valuation_difference_over_and_under():
    eur, pct = calc.valuation_difference(440_000, 400_000)
    assert eur == 40_000 and pct == pytest.approx(0.10)
    eur, pct = calc.valuation_difference(380_000, 400_000)
    assert eur == -20_000 and pct == pytest.approx(-0.05)


# disposable income and capacity

def test_living_costs_couple_with_children():
    assert calc.living_costs("Married", 2, 1200, 1800, 400) == 2600
    assert calc.living_costs("single", 0, 1200, 1800, 400) == 1200
    assert calc.living_costs(None, 1, 1200, 1800, 400) == 1600


def test_disposable_income():
    # 6,000 gross * (1 - 0.30) = 4,200 net - 300 - 1,500 - 1,800 = 600
    assert calc.disposable_income(6000, 0.30, 300, 1500, 1800) == pytest.approx(600)


def test_borrowing_capacity_limited_by_lti():
    result = calc.borrowing_capacity(gross_yearly_income=60_000, monthly_debts=0, deposit=50_000,
                                     max_lti=4.0, max_dti=0.35, max_ltv=0.90,
                                     stressed_rate_pct=6.0, term_years=30)
    assert result["lti_cap"] == pytest.approx(240_000)
    assert result["deposit_ltv_cap"] == pytest.approx(450_000)
    # 1,750/month at 6% over 30y: 200,000 * 1,750 / 1,199.10 = ~291,885
    assert result["stressed_dti_cap"] == pytest.approx(291_885, abs=2)
    assert result["estimate"] == pytest.approx(240_000)
    assert result["limited_by"] == "lti_cap"


def test_borrowing_capacity_limited_by_small_deposit():
    result = calc.borrowing_capacity(60_000, 0, 10_000, 4.0, 0.35, 0.90, 6.0, 30)
    assert result["estimate"] == pytest.approx(90_000)
    assert result["limited_by"] == "deposit_ltv_cap"


def test_borrowing_capacity_debts_exceed_dti_room():
    result = calc.borrowing_capacity(24_000, 1000, 100_000, 4.0, 0.35, 0.90, 6.0, 30)
    assert result["stressed_dti_cap"] == 0
    assert result["estimate"] == 0


# threshold flags

def test_threshold_breach_message():
    check = calc.check_threshold("DTI", 0.41, 0.35)
    assert check.breached
    assert check.message == "DTI 41% exceeds limit 35%"


def test_threshold_within_limit():
    check = calc.check_threshold("LTV", 0.80, 0.90)
    assert not check.breached
    assert check.message == "LTV 80% within limit 90%"


def test_threshold_exactly_at_limit_is_not_breach():
    # tiny float errors at the limit are not a breach
    assert not calc.check_threshold("DTI", 0.1 + 0.25, 0.35).breached


def test_threshold_ratio_format():
    check = calc.check_threshold("LTI", 4.2, 4.0, as_percent=False)
    assert check.breached
    assert check.message == "LTI 4.20x exceeds limit 4.00x"


def test_threshold_decimal_percent_format():
    assert calc.check_threshold("DTI", 0.415, 0.35).message == "DTI 41.5% exceeds limit 35%"
