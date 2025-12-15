"""
Test script to verify hints are loaded from ontology
Run this to check if your ontology hints are working
"""
from utils.ontology_loader import get_quadratic_equations, get_hints

# Load equations
equations = get_quadratic_equations()

print("=" * 60)
print("TESTING ONTOLOGY HINTS")
print("=" * 60)

for i, eq in enumerate(equations):
    print(f"\n📝 Equation {i+1}: {eq.name}")
    print("-" * 60)

    # Get hints
    hints = get_hints(eq)

    # Check each hint
    hint_steps = ['step1', 'step2', 'step3', 'step4', 'step5', 'solution']

    for step in hint_steps:
        hint_text = hints.get(step)
        if hint_text:
            print(f"✅ {step}: {hint_text[:60]}...")
        else:
            print(f"❌ {step}: MISSING - will use default hardcoded hint")

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

# Count missing hints
total_hints = len(equations) * 6
missing_hints = sum(
    1 for eq in equations for step in hint_steps if not get_hints(eq).get(step))

if missing_hints == 0:
    print("✅ ALL HINTS LOADED FROM ONTOLOGY!")
    print("   No hardcoded fallbacks will be used.")
else:
    print(f"⚠️  {missing_hints}/{total_hints} hints missing from ontology")
    print(f"   These will use hardcoded fallback hints.")
    print(f"\n   Make sure all equations have these object properties:")
    print(f"   - hasHintStep1, hasHintStep2, hasHintStep3")
    print(f"   - hasHintStep4, hasHintStep5, hasHintSolution")
