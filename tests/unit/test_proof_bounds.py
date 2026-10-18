"""Integer proof boundaries retain raw doubles without accepting a real gap."""

from copy import deepcopy
from pathlib import Path

import pytest

from scheduling.evaluation.cases import load_cases
from scheduling.evaluation.scoring import check_reference, reference
from scheduling.explanations import explain_solver
from scheduling.proof_bounds import integer_bound_proves_value
from scheduling.solver import SolverLimits


@pytest.mark.parametrize('value,bound,expected', [
    (4, 3.999999999999999, True), (4, 4.0, True), (4, 3.5, True),
    (4, 3.0, False), (4, 4.000000000000001, False),
    (0, -0.5, True), (0, -1.0, False),
    (4, float('nan'), False), (4, float('inf'), False),
    (4, 10**400, False), (4, True, False), (True, 1.0, False), (4, '4', False),
    (2**53, float(2**53 - 1), False), (2**53, float(2**53), True),
    (2**53 + 1, float(2**53), False),
])
def test_integer_proof_boundary(value, bound, expected):
    assert integer_bound_proves_value(value, bound) is expected


@pytest.fixture(scope='module', params=['dg-beec9576395b9d2472c98ea3', 'dg-7fe514bfb9687057bb68b14e'])
def numeric_regression(request):
    path = Path(__file__).resolve().parents[2] / 'benchmarks/fixtures/diverse-generation-v1/cases.json'
    case = next(c for c in load_cases(path) if c.case_id == request.param)
    result = reference(case, SolverLimits(60))
    assert case.expected_objective in ((4,), (13,))
    return case, result


def test_real_cp_sat_reference_and_explanation_preserve_raw_bound(numeric_regression):
    case, record = numeric_regression
    assert check_reference(case, record) == ('SAT', case.expected_objective, (0,))
    raw = record['result']['stages'][0]['best_bound']
    assert record['result']['stages'][0]['integer_lower_bound'] == case.expected_objective[0]
    explanation = explain_solver(case.problem, record['result'])
    assert explanation['optimality_proven']
    assert record['result']['stages'][0]['best_bound'] == raw
    assert explanation['stages'][0]['best_bound'] == raw


@pytest.mark.parametrize('field,value', [('best_bound', 3.0), ('best_bound', 4.1),
                                        ('proven_optimal', False), ('solver_status', 'FEASIBLE')])
def test_reference_and_explanation_reject_unsubstantiated_proof(numeric_regression, field, value):
    case, original = numeric_regression
    record = deepcopy(original)
    record['result']['stages'][0][field] = value
    with pytest.raises(ValueError, match='Unsubstantiated reference optimality'):
        check_reference(case, record)
    assert not explain_solver(case.problem, record['result'])['optimality_proven']


@pytest.mark.parametrize('value,bound,native,expected', [
    (13, 13.000000000000002, 13, True),
    (4, 3.999999999999999, 4, True),
    (13, 13.000000000000002, None, False),
    (13, 13.000000000000002, 12, False),
    (4, 3.0, 4, False), (4, 4.1, 4, False),
    (4, 4.0, True, False), (4, 4.0, 4.0, False),
    (2**53, float(2**53 - 1), 2**53, False),
])
def test_native_integer_evidence_not_double_tolerance_proves_optimum(value, bound, native, expected):
    assert integer_bound_proves_value(value, bound, native) is expected
