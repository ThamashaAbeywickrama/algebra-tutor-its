from owlready2 import get_ontology

# Load ontology
ONTOLOGY_PATH = "/AI/Algebra/algebra_tutor2.owl"
onto = get_ontology(ONTOLOGY_PATH).load()


def get_linear_equations():
    return [eq for eq in onto.individuals() if onto.LinearEquation in eq.is_a]


def get_quadratic_equations():
    return [eq for eq in onto.individuals() if onto.QuadraticEquation in eq.is_a]


def get_equation_data(eq):
    data = {
        "expression": eq.hasExpression[0] if hasattr(eq, 'hasExpression') and eq.hasExpression else 'Unknown',
        "degree": int(eq.hasDegree[0]) if hasattr(eq, 'hasDegree') and eq.hasDegree else 1
    }

    # Linear equation properties
    if hasattr(eq, 'hasConstant') and eq.hasConstant:
        data['constant'] = int(eq.hasConstant[0])
    if hasattr(eq, 'hasCoefficient') and eq.hasCoefficient:
        data['coefficient'] = int(eq.hasCoefficient[0])
    if hasattr(eq, 'hasSolution') and eq.hasSolution:
        data['solution'] = float(eq.hasSolution[0])

    # Quadratic equation properties
    if hasattr(eq, 'hasACoefficient') and eq.hasACoefficient:
        data['a_coefficient'] = int(eq.hasACoefficient[0])
    if hasattr(eq, 'hasBCoefficient') and eq.hasBCoefficient:
        data['b_coefficient'] = int(eq.hasBCoefficient[0])
    if hasattr(eq, 'hasCCoefficient') and eq.hasCCoefficient:
        data['c_coefficient'] = int(eq.hasCCoefficient[0])
    if hasattr(eq, 'hasSolution1') and eq.hasSolution1:
        data['solution1'] = float(eq.hasSolution1[0])
    if hasattr(eq, 'hasSolution2') and eq.hasSolution2:
        data['solution2'] = float(eq.hasSolution2[0])
    if hasattr(eq, 'hasDiscriminant') and eq.hasDiscriminant:
        data['discriminant'] = int(eq.hasDiscriminant[0])

    # Step expressions for display
    if hasattr(eq, 'hasStep4Expression') and eq.hasStep4Expression:
        data['step4_expression'] = eq.hasStep4Expression[0]
    if hasattr(eq, 'hasStep5Expression') and eq.hasStep5Expression:
        data['step5_expression'] = eq.hasStep5Expression[0]
    if hasattr(eq, 'hasStep6Expression') and eq.hasStep6Expression:
        data['step6_expression'] = eq.hasStep6Expression[0]

    return data


def get_hints(eq):
    hints = {}

    def extract_hint(hint_property_name):
        try:
            if hasattr(eq, hint_property_name):
                hint_vals = getattr(eq, hint_property_name)
                if hint_vals and len(hint_vals) > 0:
                    hint_obj = hint_vals[0]
                    if hasattr(hint_obj, 'hasHintText') and hint_obj.hasHintText:
                        return hint_obj.hasHintText[0]
                    elif isinstance(hint_obj, str):
                        return hint_obj
        except Exception as e:
            print(f"Error extracting hint {hint_property_name}: {e}")
        return None

    def extract_adaptive_hint(hint_property_name, level):
        try:
            if hasattr(eq, hint_property_name):
                hint_vals = getattr(eq, hint_property_name)
                if hint_vals and len(hint_vals) > 0:
                    hint_obj = hint_vals[0]

                    level_property = f'hasHint{level.capitalize()}'

                    if hasattr(hint_obj, level_property):
                        hint_text = getattr(hint_obj, level_property)
                        if hint_text and len(hint_text) > 0:
                            return hint_text[0]
        except Exception as e:
            print(
                f"Error extracting adaptive hint {hint_property_name} ({level}): {e}")
        return None

    # Extract old-style hints (for backward compatibility)
    hints['step1'] = extract_hint('hasHintStep1')
    hints['step2'] = extract_hint('hasHintStep2')
    hints['step3'] = extract_hint('hasHintStep3')
    hints['step4'] = extract_hint('hasHintStep4')
    hints['step5'] = extract_hint('hasHintStep5')
    hints['solution'] = extract_hint('hasHintSolution')

    # Extract adaptive hints (new)
    hints['step1_low'] = extract_adaptive_hint('hasHintStep1', 'low')
    hints['step1_moderate'] = extract_adaptive_hint('hasHintStep1', 'moderate')
    hints['step1_high'] = extract_adaptive_hint('hasHintStep1', 'high')

    hints['step2_low'] = extract_adaptive_hint('hasHintStep2', 'low')
    hints['step2_moderate'] = extract_adaptive_hint('hasHintStep2', 'moderate')
    hints['step2_high'] = extract_adaptive_hint('hasHintStep2', 'high')

    hints['step3_low'] = extract_adaptive_hint('hasHintStep3', 'low')
    hints['step3_moderate'] = extract_adaptive_hint('hasHintStep3', 'moderate')
    hints['step3_high'] = extract_adaptive_hint('hasHintStep3', 'high')

    hints['step4_low'] = extract_adaptive_hint('hasHintStep4', 'low')
    hints['step4_moderate'] = extract_adaptive_hint('hasHintStep4', 'moderate')
    hints['step4_high'] = extract_adaptive_hint('hasHintStep4', 'high')

    hints['step5_low'] = extract_adaptive_hint('hasHintStep5', 'low')
    hints['step5_moderate'] = extract_adaptive_hint('hasHintStep5', 'moderate')
    hints['step5_high'] = extract_adaptive_hint('hasHintStep5', 'high')

    hints['solution_low'] = extract_adaptive_hint('hasHintSolution', 'low')
    hints['solution_moderate'] = extract_adaptive_hint(
        'hasHintSolution', 'moderate')
    hints['solution_high'] = extract_adaptive_hint('hasHintSolution', 'high')

    return hints


def get_performance_levels():
    try:
        levels = {}
        for individual in onto.individuals():
            if onto.PerformanceLevel in individual.is_a:
                levels[individual.name] = individual
        return levels
    except Exception as e:
        print(f"Error getting performance levels: {e}")
        return {}
