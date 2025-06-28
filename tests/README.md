# PyWeb Test Suite

מערכת טסטים מסודרת עבור פרויקט PyWeb.

## מבנה הטסטים

- `test_dom.py` - טסטים עבור מערכת ה-DOM (Element, Event, כל סוגי האלמנטים)
- `test_html_parser.py` - טסטים עבור מנתח ה-HTML
- `test_render.py` - טסטים עבור מערכת הרינדור וההצגה
- `test_window.py` - טסטים עבור מערכת החלון (Console, Document, Location)
- `test_network.py` - טסטים עבור פונקציונליות הרשת
- `test_integration.py` - טסטים משולבים של כל המערכת

## הרצת הטסטים

### הרצת כל הטסטים:
```bash
python tests/run_all_tests.py
```

### הרצת טסט ספציפי:
```bash
python -m unittest tests.test_dom
python -m unittest tests.test_html_parser
python -m unittest tests.test_render
```

### הרצת טסט בודד:
```bash
python -m unittest tests.test_dom.TestElement.test_element_creation
```

## מה הטסטים בודקים

### DOM Tests (`test_dom.py`)
- יצירת אלמנטים וקיום אטריביוטים
- הוספת ילדים (טקסט ואלמנטים)
- מערכת אירועים ו-event bubbling
- פירוק סגנונות CSS
- כל סוגי האלמנטים (Div, P, Button, וכו')
- TAG_MAP ומיפוי התגיות

### HTML Parser Tests (`test_html_parser.py`)
- פירוק HTML פשוט ומורכב
- טיפול באטריביוטים
- יחסי הורה-ילד
- טיפול ברווחים ובתגיות לא ידועות
- מבנה מסמכים מלאים

### Render Tests (`test_render.py`)
- פירוק סגנונות ל-Tkinter
- סינון אפשרויות widget
- רינדור אלמנטים שונים
- רכיבים מקוננים
- טיפול באלמנטים לא ידועים

### Window Tests (`test_window.py`)
- Console logging
- Document manipulation
- Location/navigation
- Window dialogs (alert, confirm, prompt)

### Network Tests (`test_network.py`)
- שליפת HTML מהרשת
- טיפול בשגיאות רשת

### Integration Tests (`test_integration.py`)
- פרסינג מלא של HTML ל-DOM
- טסט על הקובץ האמיתי של hub

## בעיות ידועות שהטסטים מגלים

1. **באג ב-`Input` class**: `Input.__init__` יוצר 'button' במקום 'input'
2. **תגיות חסרות ב-render**: `header`, `main`, `section` לא מטופלות כראוי
3. **טיפול לא מלא ב-`<li>` tags**
4. **בעיות ב-event system**: יש לבדוק את המימוש
5. **חסרות תכונות ב-Document class**

## הוספת טסטים חדשים

כדי להוסיף טסט חדש:

1. צור קובץ חדש בשם `test_<feature>.py`
2. יבא את unittest ואת המודולים הרלוונטיים
3. הוסף את project root ל-sys.path
4. צור classes עם שם `Test<FeatureName>(unittest.TestCase)`
5. כתב methods עם שם `test_<specific_feature>`

## דרישות

- Python 3.7+
- tkinter (בדרך כלל מותקן עם Python)
- unittest (חלק מספרייה סטנדרטית)

## הערות

- הטסטים משתמשים ב-mocking כדי למנוע פתיחת חלונות Tkinter בפועל
- כמה טסטים עשויים להיכשל עקב bugs קיימים בקוד - זה מצופה ועוזר לזהות בעיות 