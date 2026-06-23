# Worksheet Design Prompts for Canva

## Data Science: Model-to-SQL Conversion Checklist

**Design Style:** Clean, technical, step-by-step. Use code blocks. Minimalist.

**Canva Prompt:**
```
Create a professional worksheet PDF (A4, landscape) for "{worksheet_title}"

Layout:
- Header (top 20%): Title + tagline about applying ML to production
- 5 sections in vertical stack, each with:
  - Section number + title (bold, #1-5)
  - Bulleted prompts or template code
  - Space for handwritten notes on right side

Colors: Dark blue (#1E3A8A) headers, light gray background, monospace font for code

Sections:
1. Model Type Assessment
   - What model did you train? (Linear Reg / Logistic / Tree / Ensemble / Other)
   - What framework? (sklearn / XGBoost / LightGBM / TensorFlow / etc)
   - Is translation practical? (Most sklearn + XGBoost are. Neural nets less so.)

2. Feature Inventory
   - List all features used in training
   - For each: WHERE does it live? (Warehouse table? Computed field?)
   - Any transformations? (scaling, binning, encoding — track these exactly)

3. SQL Translation Template
   SELECT
       {id_column},
       ({model_expression}) AS {prediction_column}
   FROM {source_table}
   WHERE {optional_filter};

4. Validation Checklist
   - Run translated SQL on sample data
   - Compare outputs to Python model.predict()
   - Diff < 0.0001? ✅ Good. > threshold? Debug preprocessing.
   - Check edge cases: nulls, outliers, extreme values

5. Deployment Prep
   - Store SQL query in version control
   - Document: input features, assumptions, last validation date
   - Set up: scheduled run frequency, alert on schema changes
   - Who owns this? (data eng or you)

Footer: "🔗 Get the full guide + community feedback in comments below"
```

---

## Life & Self-Dev: Design Your Check-in for Your Worst Day

**Design Style:** Warm, reflective, spacious. Hand-drawn elements optional. Readable fonts.

**Canva Prompt:**
```
Create a reflective worksheet PDF (A4, portrait) for "{worksheet_title}"

Layout:
- Header (top 15%): Soft gradient background. Title + subtitle about personal growth.
- 5 sections vertically stacked, each with:
  - Section title (warm orange or teal accent)
  - Reflective prompt in italics
  - Blank space for handwritten response (30-50% of section height)
  - Dividing line between sections

Colors: Warm cream background (#FFFBF0), teal accents (#0D9488), dark gray text

Sections:
1. The Problem: Best Day Self vs. Worst Day Self
   Prompt: "When were you LAST tired, stressed, or busy? Could you still do your check-in then? (Be honest.)"
   [Large blank space for reflection]

2. Minimum Viable Check-in
   Prompt: "On your worst day, with 2 minutes and zero energy, what's the SMALLEST version of this habit that still serves you? Write it below (not what you wish you'd do — what you'll actually do):"
   [Large blank space]

3. Reframe: Measure → Orient
   Prompt: "Instead of 'How did I do today?' ask 'Where am I right now?' What's one question that helps you LOCATE yourself, not grade yourself?"
   [Medium blank space]

4. The Flexibility Trap
   Prompt: "Pick ONE anchor time (not 'whenever I have time'). After coffee? Before bed? During lunch?"
   [Medium blank space]

5. The Real Metric
   Prompt: "What does 90% commitment actually look like for you—not in theory, in reality?"
   [Medium blank space]

Footer: "Reply with your answers to refine your system together."

Optional: Soft watercolor accent in corner.
```

---

## Integration Notes

- DS worksheet: Share on IG caption → link to landing page → collect email → PDF delivery
- Life worksheet: Share on IG caption → link to landing page → collect email → PDF delivery
- Poetry: Skip worksheet (commentary-only format)

**ConvertKit Landing Page Required:**
- Form collects email
- Delivers PDF + welcome email with CTA to blog
