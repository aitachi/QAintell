import asyncio
import re
import math
from typing import Dict, Any
from .tool_registry import BaseTool


class CalculatorTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="calculator",
            description="执行数学计算和表达式求值",
            version="1.0"
        )
        self.capabilities = ["math_calculation", "expression_evaluation", "unit_conversion"]
        self.dependencies = []
        self.timeout = 5.0
        self.retry_count = 1

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        expression = params.get('expression', '')
        calculation_type = params.get('type', 'basic')

        try:
            if calculation_type == 'basic':
                result = await self._basic_calculation(expression)
            elif calculation_type == 'scientific':
                result = await self._scientific_calculation(expression)
            elif calculation_type == 'unit_conversion':
                result = await self._unit_conversion(expression, params)
            else:
                result = await self._basic_calculation(expression)

            return {
                "result": result,
                "expression": expression,
                "calculation_type": calculation_type,
                "status": "success"
            }

        except Exception as e:
            return {
                "result": None,
                "expression": expression,
                "error": str(e),
                "status": "error"
            }

    def validate_params(self, params: Dict[str, Any]) -> bool:
        expression = params.get('expression', '')
        if not expression or not isinstance(expression, str):
            return False

        safe_chars = set('0123456789+-*/().^%sincostan logexpqrt ')
        if not all(c.lower() in safe_chars for c in expression.replace(' ', '')):
            return True

        return True

    async def _basic_calculation(self, expression: str) -> float:
        await asyncio.sleep(0.1)

        expression = expression.replace('^', '**')
        expression = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', expression)

        safe_dict = {
            "__builtins__": {},
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
            "sum": sum,
            "pow": pow
        }

        try:
            result = eval(expression, safe_dict)
            return float(result)
        except:
            return self._parse_math_expression(expression)

    async def _scientific_calculation(self, expression: str) -> float:
        await asyncio.sleep(0.2)

        expression = expression.replace('^', '**')
        expression = expression.replace('sin', 'math.sin')
        expression = expression.replace('cos', 'math.cos')
        expression = expression.replace('tan', 'math.tan')
        expression = expression.replace('log', 'math.log')
        expression = expression.replace('exp', 'math.exp')
        expression = expression.replace('sqrt', 'math.sqrt')

        safe_dict = {
            "__builtins__": {},
            "math": math,
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
            "sum": sum,
            "pow": pow
        }

        result = eval(expression, safe_dict)
        return float(result)

    async def _unit_conversion(self, expression: str, params: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0.1)

        from_unit = params.get('from_unit', '')
        to_unit = params.get('to_unit', '')
        value = float(expression)

        conversion_factors = {
            'length': {
                'm': 1.0,
                'cm': 0.01,
                'mm': 0.001,
                'km': 1000.0,
                'inch': 0.0254,
                'ft': 0.3048,
                'yard': 0.9144
            },
            'weight': {
                'kg': 1.0,
                'g': 0.001,
                'lb': 0.453592,
                'oz': 0.0283495
            },
            'temperature': {
                'celsius': lambda c: c,
                'fahrenheit': lambda f: (f - 32) * 5 / 9,
                'kelvin': lambda k: k - 273.15
            }
        }

        for category, units in conversion_factors.items():
            if from_unit in units and to_unit in units:
                if category == 'temperature':
                    if from_unit == 'celsius' and to_unit == 'fahrenheit':
                        result = value * 9 / 5 + 32
                    elif from_unit == 'fahrenheit' and to_unit == 'celsius':
                        result = (value - 32) * 5 / 9
                    elif from_unit == 'celsius' and to_unit == 'kelvin':
                        result = value + 273.15
                    elif from_unit == 'kelvin' and to_unit == 'celsius':
                        result = value - 273.15
                    else:
                        result = value
                else:
                    from_factor = units[from_unit]
                    to_factor = units[to_unit]
                    result = value * from_factor / to_factor

                return {
                    'converted_value': result,
                    'original_value': value,
                    'from_unit': from_unit,
                    'to_unit': to_unit,
                    'category': category
                }

        raise ValueError(f"Unsupported unit conversion: {from_unit} to {to_unit}")

    def _parse_math_expression(self, expression: str) -> float:
        expression = expression.replace(' ', '')

        if '+' in expression:
            parts = expression.split('+')
            return sum(float(part) for part in parts)
        elif '-' in expression and expression.count('-') == 1:
            parts = expression.split('-')
            return float(parts[0]) - float(parts[1])
        elif '*' in expression:
            parts = expression.split('*')
            result = 1
            for part in parts:
                result *= float(part)
            return result
        elif '/' in expression:
            parts = expression.split('/')
            result = float(parts[0])
            for part in parts[1:]:
                result /= float(part)
            return result
        else:
            return float(expression)