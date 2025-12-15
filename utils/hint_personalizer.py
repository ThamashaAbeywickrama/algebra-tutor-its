# FILE 2: utils/hint_personalizer.py (CREATE NEW FILE)

def get_adaptive_hint(ontology_hints, performance_level, step_key):
    # Try to get adaptive hint from ontology first
    adaptive_key = f'{step_key}_{performance_level}'
    if adaptive_key in ontology_hints and ontology_hints[adaptive_key]:
        return ontology_hints[adaptive_key]

    # Fallback to default behavior
    return get_default_hint(performance_level, step_key)


def get_default_hint(performance_level, step_key):
    # Linear equation hints
    linear_hints = {
        'low': {
            'step1': "The constant is the number added or subtracted from x in the equation. Look for the number that stands ALONE without any x attached. For example, in 2x + 3 = 7, the number 3 is the constant because it's not with x.",
            'step2': "The coefficient is the number that is MULTIPLIED by the variable x. Look for the number directly attached to x (no space). In 2x + 3, the 2 is the coefficient because it shows we have 2 x's.",
            'step3': "To find x, you need to isolate it. First, subtract the constant from both sides. Then divide both sides by the coefficient. For example: 2x + 3 = 7 becomes 2x = 4, then x = 2."
        },
        'moderate': {
            'step1': "The constant is the number added or subtracted from x.",
            'step2': "The coefficient is the number multiplied by x.",
            'step3': "Subtract the constant from both sides, then divide by the coefficient."
        },
        'high': {
            'step1': "Identify the constant term.",
            'step2': "Identify the coefficient of x.",
            'step3': "Use inverse operations to isolate x."
        }
    }

    # Quadratic equation hints
    quadratic_hints = {
        'low': {
            'step1': "Match your equation with axÂ² + bx + c = 0. The 'a' is the coefficient of xÂ² (number in front of x²). The 'b' is the coefficient of x (number in front of x, don't forget negative signs!). The 'c' is the constant (number by itself).",
            'step2': "Take the 'a' value (coefficient of xÂ²) and multiply it by the 'c' value (constant). This gives you the AC product. For example, if a = 2 and c = 6, then AC = 12.",
            'step3': "Find two numbers that multiply to AC AND add to b. List factor pairs of AC. For each pair, check if they add to b. Consider positive and negative combinations.",
            'step4': "Take the middle term (bx) and split it using your two numbers. Write the equation with four terms, then group the first two and last two terms together.",
            'step5': "From the first group, pull out what's common (factor out). From the second group, pull out what's common. You should see the same binomial in both groups.",
            'solution': "Set each factor equal to zero. Solve each equation separately. For example, if (x-2)(x-3)=0, then x-2=0 (x=2) and x-3=0 (x=3)."
        },
        'moderate': {
            'step1': "Extract coefficients a, b, c from axÂ² + bx + c = 0.",
            'step2': "Calculate the AC product.",
            'step3': "Find two numbers that multiply to AC and add to b.",
            'step4': "Split the middle term bx using your two numbers.",
            'step5': "Factor by grouping.",
            'solution': "Set each factor to zero and solve."
        },
        'high': {
            'step1': "Find a, b, c.",
            'step2': "Calculate AC.",
            'step3': "Factor pair search.",
            'step4': "Decompose bx.",
            'step5': "Factor by grouping.",
            'solution': "Solve each factor."
        }
    }

    # Determine if linear or quadratic based on step_key
    if step_key in ['step1', 'step2', 'step3', 'solution']:
        # For linear equations - steps 0-2 map to step1-step3
        hint_dict = linear_hints.get(
            performance_level, linear_hints['moderate'])
    else:
        # For quadratic equations
        hint_dict = quadratic_hints.get(
            performance_level, quadratic_hints['moderate'])

    return hint_dict.get(step_key, "Keep trying! You're doing great!")


def personalize_hint_for_linear(hint_text, performance_level):

    if performance_level == 'low':
        # Already detailed, return as is or expand
        return hint_text
    elif performance_level == 'high':
        # Make concise - keep only essential info
        if "constant" in hint_text.lower():
            return "Identify the constant term."
        elif "coefficient" in hint_text.lower():
            return "Identify the coefficient of x."
        elif "solve" in hint_text.lower() or "isolate" in hint_text.lower():
            return "Use inverse operations to isolate x."
        else:
            return hint_text
    else:  # moderate
        return hint_text


def get_hint_for_performance(ontology_hints, performance_level, equation_type, step):

    step_map = {
        0: 'step1',
        1: 'step2',
        2: 'step3',
        3: 'step4',
        4: 'step5',
        5: 'solution'
    }

    step_key = step_map.get(step, 'step1')

    # Try adaptive hint first
    hint = get_adaptive_hint(ontology_hints, performance_level, step_key)

    return hint if hint else "Try again! You're doing great!"
