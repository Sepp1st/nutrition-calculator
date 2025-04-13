import nutrition_calculator as project
import csv

def test_Food_macros():
    with open("Food.csv","r") as file:
            reader=csv.DictReader(file)
            food_data={row["Description"]:row for row in reader}
            assert project.Food_macros(50, "egg", food_data)==[11,5,7]
            assert project.Food_macros(500,"lettuce", food_data)==[6,14,1]


def test_Macros_left():
    assert project.Macros_left(55,0,0)==["fish", "dairy", "lean meats"]
    assert project.Macros_left(0,55,0)==["fruits", "veggies", "whole grains"]
    assert project.Macros_left(55,55,0)==["fish", "dairy", "lean meats", "fruits", "veggies", "whole grains"]


def test_Macros_goal():
    assert project.Macros_goal(1407)==[87,140,54]
    assert project.Macros_goal(1420)==[88,142,55]