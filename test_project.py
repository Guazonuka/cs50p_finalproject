from project import check_start_date, check_end_date, create_date_list
import pytest

def test_check_start_date(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: "2020-01-01")
    result = check_start_date()
    assert result == "2020-01-01"
    monkeypatch.setattr('builtins.input', lambda _: " 2022-01-01  ")
    result = check_start_date()
    assert result == "2022-01-01"
    

def test_check_end_date(monkeypatch):
    start_dt = '2023-10-01'
    monkeypatch.setattr('builtins.input', lambda _: '2023-10-03')
    result = check_end_date(start_dt)
    assert result == '2023-10-03'


def test_create_date_list(monkeypatch):
    start_dt = '2023-10-01'
    end_dt = '2023-10-03'
    inputs = iter(['2023-10-01', '2023-10-03'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    results = create_date_list(start_dt, end_dt)
    assert results == ['2023-10-01', '2023-10-02', '2023-10-03']