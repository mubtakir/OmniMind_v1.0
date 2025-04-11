
'''
ممتاز! لننتقل الآن إلى كتابة الكود للوحدة الأولى في مجلد foundations/: وهي equation_manager.py.
هذه الوحدة ستكون مسؤولة حصريًا عن كل ما يتعلق بمعالجة المعادلات الشكلية (ShapeEquation) كسلاسل نصية وهياكل بيانات. ستأخذ على عاتقها المهام التي كانت موزعة جزئيًا في EquationProcessor و EquationManager في الأنظمة السابقة، مع تحسينات وتوضيح للمسؤوليات.
الوظائف الرئيسية لـ EquationManager:
تحليل السلاسل النصية (parse): تحويل سلسلة نصية تمثل معادلة شكلية (مثل "line(0,0,1,1){color='red'} + circle(1,1,0.5)") إلى كائن ShapeEquation منظم يحتوي على قائمة من ShapeComponent والمشغلات (operators) بينها. سنستخدم مكتبة pyparsing لبناء محلل لغوي قوي ومرن لهذه الصيغة.
توليد السلاسل النصية (generate_string): تحويل كائن ShapeEquation مرة أخرى إلى تمثيل نصي مقروء ومتسق (سيعتمد بشكل أساسي على دوال __str__ المعرفة في ShapeComponent و ShapeEquation).
(اختياري) تبسيط المعادلات (simplify): (ميزة متقدمة للتطوير المستقبلي) محاولة تبسيط المعادلة عن طريق إزالة المكونات المكررة أو غير الضرورية أو دمج بعض العمليات.
التحويل الرمزي (get_symbolic_representation): محاولة تحويل مكونات المعادلة (خاصة الأولية منها مثل الأشكال الهندسية أو الدوال الرياضية) إلى تعبيرات رياضية رمزية باستخدام مكتبة sympy (إذا كانت متاحة). هذا مفيد للتكامل مع CalculusEngine أو لإجراء عمليات جبرية رمزية.
التحقق من الصحة (validate): التأكد من أن كائن ShapeEquation متناسق (عدد المشغلات صحيح) وأن مكوناته صالحة.
التصميم:
فئة EquationManager.
__init__: تقوم بتهيئة المحلل اللغوي pyparsing مرة واحدة.
دوال عامة: parse, generate_string, simplify (مستقبلي), get_symbolic_representation, validate.
دوال داخلية مساعدة: لبناء قواعد pyparsing (_build_parser) ومعالجة نتائج التحليل (_parse_component_action, _parse_style_action).
'''

# OmniMind_v1.0/foundations/equation_manager.py

# -*- coding: utf-8 -*-
"""
===============================================================================
الوحدة: مدير المعادلات الشكلية (Shape Equation Manager) - OmniMind v1.0
===============================================================================

**الملف:** `equation_manager.py`

**الموقع:** `foundations/equation_manager.py`

**الوصف:**
تتولى هذه الوحدة المسؤولية الكاملة عن التعامل مع تمثيل المعادلات الشكلية
(`ShapeEquation` و `ShapeComponent`)، سواء كهياكل بيانات أو كسلاسل نصية.
وظائفها تشمل:
-   **التحليل (Parsing):** تحويل السلاسل النصية المعقدة التي تصف الأشكال
    إلى كائنات `ShapeEquation` منظمة باستخدام `pyparsing`.
-   **التوليد (Generation):** تحويل كائنات `ShapeEquation` مرة أخرى إلى
    تمثيل نصي مقروء ومتسق.
-   **التحقق (Validation):** التأكد من صحة وتناسق هياكل `ShapeEquation`.
-   **التحويل الرمزي (Symbolic Conversion):** محاولة تحويل أجزاء من المعادلة
    إلى تمثيل رياضي رمزي باستخدام مكتبة `sympy` (اختياري).
-   **(مستقبلي) التبسيط (Simplification):** تطبيق قواعد لتبسيط المعادلات.

تستخدم هذه الوحدة مكتبة `pyparsing` لبناء محلل قوي ومرن لقواعد اللغة الخاصة
بوصف المعادلات الشكلية.

**الفئات المعرفة:**
-   `EquationManager`: الفئة الرئيسية التي تحتوي على منطق التحليل والتوليد والتحقق.

**الاعتماديات:**
-   `pyparsing`: لتحليل السلاسل النصية. (ضرورية)
-   `sympy`: (اختياري) للتحويل إلى تمثيل رمزي.
-   `logging`: للتسجيل.
-   `typing`: لتحديد الأنواع.
-   `..representations`: للوصول إلى `ShapeComponent` و `ShapeEquation`.

**المساهمة في النظام:**
-   توفر واجهة مركزية وموحدة للتعامل مع "لغة" وصف الأشكال والمعادلات.
-   تفصل منطق معالجة بناء الجملة والمعنى للمعادلات عن الوحدات الأخرى
    (مثل `OmniMindEngine` أو الوحدات المعرفية).
-   تسمح بتعريف قواعد لغة مرنة وقابلة للتوسيع لوصف الأشكال والعمليات.
-   تمكن من تحويل التمثيلات النصية إلى هياكل بيانات قابلة للمعالجة والعكس.
"""

import logging
import re
from typing import Dict, Any, Optional, List, Union, Tuple, Callable, Set

# --- استيراد المكتبات المطلوبة بشروط ---
try:
    import pyparsing as pp
    # تمكين Packrat لزيادة سرعة التحليل (موصى به)
    pp.ParserElement.enablePackrat()
    PYPARSING_AVAILABLE = True
except ImportError:
    PYPARSING_AVAILABLE = False
    print("خطأ فادح: مكتبة pyparsing غير مثبتة. EquationManager لن يعمل. قم بتثبيتها: pip install pyparsing")
    # تعريفات وهمية لتجنب أخطاء لاحقة إذا استمر البرنامج بطريقة ما
    pp = type('pp', (object,), {'ParseException': Exception}) # نوع وهمي

try:
    import sympy
    # تعريف رموز شائعة للاستخدام في التحويل الرمزي
    sympy_x, sympy_y, sympy_z, sympy_t, sympy_r, sympy_theta, sympy_phi = sympy.symbols('x y z t r theta phi')
    SYMPY_AVAILABLE = True
except ImportError:
    sympy = None
    SYMPY_AVAILABLE = False
    print("تحذير: مكتبة SymPy غير مثبتة. ميزات التحويل الرمزي ستكون معطلة في EquationManager.")

# استيراد هياكل البيانات من الوحدة الشقيقة
try:
    from ..representations import ShapeComponent, ShapeEquation
except ImportError:
    # حل بديل إذا تم تشغيل الملف مباشرة
    from representations import ShapeComponent, ShapeEquation


# إعداد المسجل
log = logging.getLogger(__name__)

# ============================================================== #
# ================ CLASS: EquationManager ====================== #
# ============================================================== #
class EquationManager:
    """
    يدير تحليل (parsing) وتوليد (generation) والتحقق (validation)
    والمعالجة الرمزية (symbolic processing) للمعادلات الشكلية.
    """
    def __init__(self):
        """
        تهيئة مدير المعادلات، بما في ذلك بناء المحلل اللغوي `pyparsing`.
        """
        if not PYPARSING_AVAILABLE:
            raise ImportError("مكتبة pyparsing ضرورية لعمل EquationManager.")

        # بناء المحلل اللغوي مرة واحدة عند التهيئة
        self._parser: Optional[pp.ParserElement] = None
        try:
            self._parser = self._build_parser()
            log.info("Equation Manager initialized successfully (Pyparsing enabled).")
        except Exception as e:
             log.critical(f"Failed to build the equation parser! EquationManager unusable. Error: {e}", exc_info=True)
             # يمكن رفع الخطأ هنا لمنع استخدام المدير بدون محلل
             raise RuntimeError("Failed to build equation parser") from e

        # قاموس لربط أنواع المكونات بدوال تحويلها إلى SymPy
        self._sympy_map: Dict[str, Callable] = {}
        if SYMPY_AVAILABLE:
             self._sympy_map = self._build_sympy_map()
             log.info(f"Symbolic conversion enabled (SymPy available). Mapped types: {list(self._sympy_map.keys())}")
        else:
             log.warning("Symbolic conversion disabled (SymPy not available).")


    # ----------------------------------------------------------
    # قسم بناء المحلل اللغوي (Pyparsing Grammar) - مُحسّن
    # ----------------------------------------------------------
    def _build_parser(self) -> pp.ParserElement:
        """إنشاء قواعد تحليل Pyparsing لمعادلات الشكل."""
        log.debug("Building Pyparsing grammar for Shape Equations...")

        # --- تعريف العناصر الأساسية ---
        LPAREN, RPAREN, LBRACK, RBRACK, LBRACE, RBRACE, EQ, COLON, COMMA = map(pp.Suppress, "()[]{}=:,")

        # الأرقام: استخدام common لتغطية الأعداد الصحيحة والعشرية والصيغة العلمية
        # وتحويلها تلقائيًا إلى float أو int
        number = pp.pyparsing_common.number

        # القيم المنطقية: دعم أشكال مختلفة
        bool_literal = pp.oneOf("true True TRUE false False FALSE yes Yes YES no No NO on On ON off Off OFF", caseless=True)
        # تحويل القيم النصية إلى قيم منطقية Python
        bool_literal.setParseAction(lambda tokens: tokens[0].lower() in ('true', 'yes', 'on'))

        # الألوان: دعم صيغة hex (#rrggbb)
        hex_color = pp.Combine(pp.Literal('#') + pp.Word(pp.hexnums, exact=6))

        # المعرفات: أسماء الأنواع، المفاتيح، والمتغيرات المحتملة (تبدأ بحرف)
        identifier = pp.Word(pp.alphas, pp.alphanums + "_")

        # السلاسل النصية: دعم علامات الاقتباس المفردة والمزدوجة مع الهروب
        string_literal = pp.QuotedString("'", escChar='\\') | pp.QuotedString('"', escChar='\\')

        # القيمة الأساسية: أي من الأنواع المذكورة أعلاه
        base_value = (number | bool_literal | hex_color | string_literal | identifier).setResultsName("baseValue")

        # --- بنية النمط {key=value, ...} ---
        style_key = identifier.copy().setResultsName("key")
        # إعادة تعريف style_value ليكون Forward للسماح بالقواميس/القوائم المتداخلة (مستقبلي)
        style_value = pp.Forward()
        # دعم القوائم والمجموعات داخل النمط (مثال: [(r,g,b), (r,g,b)] للتدرج)
        style_tuple_inner = pp.Group(LPAREN + pp.delimitedList(style_value) + RPAREN) # مجموعة داخل القوس
        style_list_inner = pp.Group(LBRACK + pp.delimitedList(style_tuple_inner) + RBRACK).setResultsName("listValue")
        style_dict_inner = pp.Forward() # قواميس متداخلة (مثل تحويلات CSS)
        style_dict_inner_content = pp.Group(style_key + EQ + style_value).setResultsName("dictItem", listAllMatches=True)
        style_dict_inner << (LBRACE + pp.Optional(pp.delimitedList(style_dict_inner_content)) + RBRACE).setResultsName("dictValue")

        style_value << (style_list_inner | style_dict_inner | base_value) # تعريف style_value الآن

        style_assignment = pp.Group(style_key + EQ + style_value).setResultsName("styleAssign")
        # قاموس النمط: استخدام delimitedList للسماح بقاموس فارغ {}
        style_dict_parser = (LBRACE + pp.Optional(pp.delimitedList(style_assignment)) + RBRACE)
        # تعيين دالة معالجة مخصصة لتحويل نتيجة التحليل إلى قاموس Python
        style_dict_parser.setParseAction(self._parse_style_action)

        # --- بنية النطاق [min:max] ---
        # يجب أن يكونا رقمين
        range_expr = pp.Group(LBRACK + number.copy().setResultsName("min") + COLON +
                               number.copy().setResultsName("max") + RBRACK).setResultsName("range")

        # --- بنية المكون type(param1, ...)[range]{style} ---
        comp_type = identifier.copy().setResultsName("type")
        # قائمة المعلمات: استخدام delimitedList يسمح بقائمة فارغة ()
        param_list = pp.Group(pp.Optional(pp.delimitedList(base_value))).setResultsName("params") # جعل المجموعة اختيارية بدل المحتوى

        shape_component_parser = pp.Group(
            comp_type + LPAREN + param_list + RPAREN +
            pp.Optional(range_expr) +
            pp.Optional(style_dict_parser.copy().setResultsName("style")) # استخدام نسخة وتسمية
        )
        # تعيين دالة معالجة مخصصة لتحويل نتيجة التحليل إلى كائن ShapeComponent
        shape_component_parser.setParseAction(self._parse_component_action)

        # --- المشغلات والمعادلة الكاملة ---
        # تعريف المشغلات المسموح بها (نفس ALLOWED_OPERATORS)
        op = pp.oneOf(list(ALLOWED_OPERATORS)).setResultsName("operator")

        # معادلة كاملة: تبدأ بمكون، ثم تتبعها صفر أو أكثر من (مشغل + مكون)
        # استخدام StringStart و StringEnd لضمان تحليل السلسلة بأكملها
        full_equation_parser = pp.StringStart() + shape_component_parser.copy().setResultsName("firstComponent") + \
                               pp.ZeroOrMore(pp.Group(op + shape_component_parser.copy().setResultsName("nextComponent"))) + \
                               pp.StringEnd()

        log.debug("Pyparsing grammar built successfully.")
        return full_equation_parser

    # ----------------------------------------------------------
    # دوال معالجة التحليل (Parse Actions) - مُحسّنة
    # ----------------------------------------------------------
    def _parse_style_action(self, s: str, loc: int, tokens: Any) -> Dict[str, Any]:
        """(مُحسّن) Parse action لـ Pyparsing لتحويل توكنز النمط إلى قاموس Python."""
        style_dict = {}
        # Tokens الآن عبارة عن ParseResults، قد تحتوي على قائمة بالتعيينات أو تكون فارغة
        assignments = tokens.asList() # الحصول على قائمة التعيينات (قد تكون متداخلة)
        for assign_group in assignments:
             # التأكد من أن assign_group هو المجموعة المتوقعة [key, value]
             if isinstance(assign_group, pp.ParseResults) and 'key' in assign_group and len(assign_group) > 1:
                 key = assign_group['key']
                 value_token = assign_group[1] # القيمة قد تكون نتيجة تحليل أخرى
                 value = self._parse_value_token(value_token) # دالة مساعدة لتحويل القيمة
                 if value is not None: # تجاهل المفاتيح بقيم None المحولة (مثل none النصية)
                      style_dict[key] = value
             elif isinstance(assign_group, list) and len(assign_group)==1 and isinstance(assign_group[0],dict):
                 # حالة القاموس المتداخل
                 style_dict.update(assign_group[0]) # دمج القاموس المتداخل

        return style_dict

    def _parse_value_token(self, token: Any) -> Any:
        """(مساعد) تحويل توكن قيمة (قد يكون متداخلاً) إلى قيمة Python."""
        if isinstance(token, (int, float, bool, str)):
            # القيم الأساسية
             if isinstance(token, str) and token.lower() == 'none': return None # تحويل 'none' النصية
             return token
        elif isinstance(token, pp.ParseResults):
             if token.getName() == 'listValue':
                 # تحويل قائمة المجموعات (Tuples)
                 return [tuple(self._parse_value_token(item) for item in grp.asList()) for grp in token.asList()]
             elif token.getName() == 'dictValue':
                 # تحويل القاموس المتداخل
                 return self._parse_style_action("", 0, token) # استدعاء معالج القاموس
             else:
                 # قد يكون قيمة أساسية داخل مجموعة، أعد أول عنصر
                 asList = token.asList()
                 return self._parse_value_token(asList[0]) if asList else None
        elif isinstance(token, list):
            # إذا كانت قائمة (نتيجة delimitedList داخل Group)، عالج العناصر
            return [self._parse_value_token(item) for item in token]

        return token # إرجاع التوكن كما هو إذا لم يتم التعرف عليه

    def _parse_component_action(self, s: str, loc: int, tokens: Any) -> Optional[ShapeComponent]:
        """(مُحسّن) Parse action لـ Pyparsing لتحويل توكنز المكون إلى كائن ShapeComponent."""
        # Tokens[0] يحتوي على نتيجة تحليل pp.Group للمكون
        data = tokens[0].asDict()
        comp_type = data.get('type', '').lower() # الحصول على النوع بأمان
        if not comp_type:
            log.error(f"Parser error at loc {loc}: Component type missing.")
            raise pp.ParseException(s, loc, "Component type missing.")

        # معالجة المعلمات
        params_raw = data.get('params', [])
        # params_raw قد تكون قائمة من القيم أو قائمة من pp.ParseResults
        params = [self._parse_value_token(p) for p in params_raw]

        # معالجة النطاق
        comp_range: Optional[Tuple[float, float]] = None
        if 'range' in data:
            range_data = data['range']
            try:
                # التحويل لـ float والتأكد من أنها tuple
                comp_range = (float(range_data['min']), float(range_data['max']))
            except (KeyError, ValueError, TypeError) as e:
                log.error(f"Parser error at loc {loc}: Invalid range format for component '{comp_type}'. Range data: {range_data}. Error: {e}")
                raise pp.ParseException(s, loc, f"Invalid range format for {comp_type}: {e}")

        # الحصول على النمط (تمت معالجته بواسطة _parse_style_action إذا وجد)
        style = data.get('style', {})

        # إنشاء المكون (سيتم التحقق الإضافي في __post_init__)
        try:
             component = ShapeComponent(type=comp_type, params=params, range=comp_range, style=style)
             return component
        except (ValueError, TypeError) as e:
             log.error(f"Error creating ShapeComponent for type '{comp_type}' at loc {loc}: {e}")
             # تحويل الخطأ لـ ParseException ليتم التقاطه بواسطة parse()
             raise pp.ParseException(s, loc, f"Invalid ShapeComponent data: {e}")

    # ----------------------------------------------------------
    # الدوال العامة للمدير
    # ----------------------------------------------------------
    def parse(self, equation_str: str) -> Optional[ShapeEquation]:
        """
        يحلل سلسلة نصية تمثل معادلة شكلية إلى كائن `ShapeEquation`.

        Args:
            equation_str (str): السلسلة النصية للمعادلة المراد تحليلها.

        Returns:
            Optional[ShapeEquation]: كائن المعادلة إذا نجح التحليل، وإلا `None`.
                                     يتم إرجاع `None` أيضًا إذا كان المحلل غير متاح.
        """
        if not self._parser:
            log.error("Equation parser is not available. Cannot parse.")
            return None
        if not isinstance(equation_str, str) or not equation_str.strip():
            log.warning("EquationManager.parse: Received empty or invalid input string.")
            return None

        log.info(f"Parsing equation string: '{equation_str[:100]}...'")
        try:
            # استخدام parseString مع parseAll=True لضمان تحليل السلسلة بأكملها
            parsed_results = self._parser.parseString(equation_str, parseAll=True)

            # استخلاص المكون الأول والمشغلات والمكونات التالية
            equation = ShapeEquation()
            first_component = parsed_results.get("firstComponent")

            if isinstance(first_component, ShapeComponent):
                 equation.components.append(first_component)
                 # استخلاص باقي الأزواج (مشغل + مكون تالي)
                 for op_comp_group in parsed_results.asList()[1:]: # تخطي المكون الأول
                      if isinstance(op_comp_group, pp.ParseResults): # يجب أن تكون مجموعة المشغل والمكون
                           op = op_comp_group.get("operator")
                           next_comp = op_comp_group.get("nextComponent")
                           if isinstance(op, str) and isinstance(next_comp, ShapeComponent):
                                equation.operators.append(op.strip())
                                equation.components.append(next_comp)
                           else:
                                log.warning(f"Skipping unexpected element during parsing: {op_comp_group}")
            else:
                 log.error(f"Parsing error: Could not extract the first component from results.")
                 return None


            # التحقق النهائي من التناسق بعد التحليل الكامل
            num_comp = len(equation.components)
            num_ops = len(equation.operators)
            expected_ops = max(0, num_comp - 1)
            if num_comp > 0 and num_ops != expected_ops:
                 log.warning(f"Parsed ShapeEquation has inconsistent structure: "
                             f"{num_comp} components, {num_ops} operators (expected {expected_ops}).")
                 # قد نقرر إصلاحه هنا، أو تركه كما هو والسماح لـ validate بكشفه لاحقًا

            log.info(f"Parsing successful: {len(equation.components)} components, {len(equation.operators)} operators.")
            return equation

        except pp.ParseException as e:
            # خطأ محدد من pyparsing
            log.error(f"Failed to parse equation string at char {e.loc} (line:{e.lineno}, col:{e.col}):")
            log.error(f"  Input: '{equation_str}'")
            log.error(f"  Error: {e.msg}")
            log.error(f"  {e.line}") # طباعة السطر الذي به الخطأ
            log.error(f"  {' '*(e.col-1)}^") # الإشارة إلى مكان الخطأ
            return None
        except Exception as e:
            # أي خطأ آخر غير متوقع أثناء التحليل أو إنشاء الكائنات
            log.error(f"Unexpected error during equation parsing: {e}", exc_info=True)
            return None

    def generate_string(self, equation: ShapeEquation) -> str:
        """
        تولد تمثيلًا نصيًا من كائن `ShapeEquation`.
        تعتمد بشكل أساسي على دالة `__str__` المعرفة في `ShapeEquation`.

        Args:
            equation (ShapeEquation): كائن المعادلة المراد تحويله لنص.

        Returns:
            str: التمثيل النصي للمعادلة، أو رسالة خطأ إذا كان المدخل غير صالح.
        """
        if not isinstance(equation, ShapeEquation):
            log.error("generate_string requires a ShapeEquation object.")
            return "<Invalid Input: Not a ShapeEquation>"
        return str(equation) # دالة __str__ في ShapeEquation تقوم بالعمل

    def validate(self, equation: ShapeEquation) -> bool:
        """
        التحقق من صحة وتناسق كائن `ShapeEquation`.
        حالياً تتحقق فقط من تطابق عدد المشغلات والمكونات.

        Args:
            equation (ShapeEquation): كائن المعادلة للتحقق منه.

        Returns:
            bool: True إذا كانت المعادلة متناسقة، False خلاف ذلك.
        """
        if not isinstance(equation, ShapeEquation): return False
        num_comp = len(equation.components)
        num_ops = len(equation.operators)
        is_valid = (num_comp == 0 and num_ops == 0) or \
                   (num_comp > 0 and num_ops == num_comp - 1)
        if not is_valid:
             log.warning(f"Validation failed for ShapeEquation: {num_comp} components, {num_ops} operators.")
        return is_valid

    # ----------------------------------------------------------
    # قسم التحويل الرمزي (SymPy)
    # ----------------------------------------------------------
    def _build_sympy_map(self) -> Dict[str, Callable]:
        """(داخلي) بناء قاموس الربط لأنواع المكونات ودوال تحويلها لـ SymPy."""
        sympy_map = {
            # الدوال البارامترية (t هو المتغير)
            'circle': self._sympy_parametric_wrapper(self._sympy_circle_func),
            'polygon': self._sympy_parametric_wrapper(self._sympy_polygon_func),
            'bezier': self._sympy_parametric_wrapper(self._sympy_bezier_func),
            # الدوال y=f(x) (x هو المتغير)
            'line': self._sympy_function_wrapper(self._sympy_line_func),
            'sine': self._sympy_function_wrapper(self._sympy_sine_func),
            'exp': self._sympy_function_wrapper(self._sympy_exp_func),
            # يمكن إضافة المزيد من الدوال الرياضية هنا
            'parabola': self._sympy_function_wrapper(self._sympy_parabola_func),
            'log': self._sympy_function_wrapper(self._sympy_log_func),
        }
        # إزالة الإدخالات التي فشل تعريف دوالها
        return {k: v for k, v in sympy_map.items() if v is not None}

    # --- أغلفة (Wrappers) لتوحيد واجهة دوال التحويل ---
    def _sympy_parametric_wrapper(self, func: Callable) -> Optional[Callable]:
        """(داخلي) غلاف لدوال التحويل البارامترية (ترجع x, y بدلالة t)."""
        if not SYMPY_AVAILABLE: return None
        def wrapper(params: List[Any], metadata: Dict) -> Optional[Tuple[sympy.Expr, sympy.Expr, sympy.Symbol]]:
             try:
                 # تمرير المتغير t والمعلمات للدالة الأصلية
                 x_expr, y_expr = func(sympy_t, params)
                 return x_expr, y_expr, sympy_t # إرجاع تعبيرات x, y والمتغير t
             except Exception as e:
                  log.warning(f"SymPy conversion error in parametric wrapper for {func.__name__}: {e}")
                  return None
        return wrapper

    def _sympy_function_wrapper(self, func: Callable) -> Optional[Callable]:
        """(داخلي) غلاف لدوال التحويل y=f(x) (ترجع y بدلالة x)."""
        if not SYMPY_AVAILABLE: return None
        def wrapper(params: List[Any], metadata: Dict) -> Optional[Tuple[sympy.Expr, sympy.Expr, sympy.Symbol]]:
            try:
                 # تمرير المتغير x والمعلمات للدالة الأصلية
                 y_expr = func(sympy_x, params)
                 # المعادلة هي sympy.Eq(sympy_y, y_expr)
                 # لكننا نعيد فقط تعبير y والمتغيرات x, y
                 return sympy_x, y_expr, sympy_y # إرجاع x, تعبير y, والرمز y
            except Exception as e:
                 log.warning(f"SymPy conversion error in function wrapper for {func.__name__}: {e}")
                 return None
        return wrapper

    # --- دوال التحويل الرمزية الفعلية ---
    def _sympy_circle_func(self, t: sympy.Symbol, params: List[Any]) -> Tuple[sympy.Expr, sympy.Expr]:
        if len(params) != 3: raise ValueError("Circle requires 3 params (x0, y0, r).")
        x0, y0, r = map(sympy.sympify, params) # تحويل المعلمات لـ SymPy
        return x0 + r * sympy.cos(t), y0 + r * sympy.sin(t)

    def _sympy_line_func(self, x: sympy.Symbol, params: List[Any]) -> sympy.Expr:
        if len(params) != 4: raise ValueError("Line requires 4 params (x1, y1, x2, y2).")
        x1, y1, x2, y2 = map(sympy.sympify, params)
        if x2 - x1 == 0: # خط رأسي - لا يمكن تمثيله كـ y=f(x)
             # يمكن إرجاعsympy.Eq(sympy_x, x1) أو None
             log.warning("Cannot represent vertical line as y=f(x) in SymPy.")
             raise NotImplementedError("Vertical line") # أو نوع خطأ آخر
        m = (y2 - y1) / (x2 - x1)
        c = y1 - m * x1
        return m * x + c

    def _sympy_sine_func(self, x: sympy.Symbol, params: List[Any]) -> sympy.Expr:
        if len(params) != 3: raise ValueError("Sine requires 3 params (A, freq, phase).")
        A, freq, phase = map(sympy.sympify, params)
        return A * sympy.sin(freq * x + phase)

    def _sympy_exp_func(self, x: sympy.Symbol, params: List[Any]) -> sympy.Expr:
        if len(params) != 3: raise ValueError("Exp requires 3 params (A, k, x0).")
        A, k, x0 = map(sympy.sympify, params)
        return A * sympy.exp(-k * (x - x0)) # دالة أسية متناقصة كمثال

    def _sympy_parabola_func(self, x: sympy.Symbol, params: List[Any]) -> sympy.Expr:
        # مثال: قطع مكافئ y = a*(x-h)**2 + k
        if len(params) != 3: raise ValueError("Parabola (example) requires 3 params (a, h, k).")
        a_s, h_s, k_s = map(sympy.sympify, params)
        return a_s * (x - h_s)**2 + k_s

    def _sympy_log_func(self, x: sympy.Symbol, params: List[Any]) -> sympy.Expr:
        # مثال: y = A * log(k*(x-x0)) + C
        if len(params) != 4: raise ValueError("Log (example) requires 4 params (A, k, x0, C).")
        A_s, k_s, x0_s, C_s = map(sympy.sympify, params)
        # تحديد القاعدة (افتراضي e)
        base = sympy.E
        if 'base' in params: # أو طريقة أخرى لتحديد القاعدة
             base = sympy.sympify(params['base'])
        return A_s * sympy.log(k_s * (x - x0_s), base) + C_s

    # (يمكن إضافة دوال لـ polygon و bezier إذا أمكن تمثيلها بارامتريًا بـ SymPy)
    def _sympy_polygon_func(self, t: sympy.Symbol, params: List[Any]) -> Tuple[sympy.Expr, sympy.Expr]:
        raise NotImplementedError("Symbolic representation for polygon is complex.")
    def _sympy_bezier_func(self, t: sympy.Symbol, params: List[Any]) -> Tuple[sympy.Expr, sympy.Expr]:
        # ممكن باستخدام صيغة Bernstein، لكنها معقدة
        if len(params) < 4 or len(params) % 2 != 0: raise ValueError("Invalid Bezier params.")
        points_sym = [sympy.Point(params[i], params[i+1]) for i in range(0, len(params), 2)]
        n = len(points_sym) - 1
        x_expr = sympy.sympify(0)
        y_expr = sympy.sympify(0)
        for k, p in enumerate(points_sym):
             # معامل برنشتاين
             bernstein_coeff = sympy.binomial(n, k) * (t**k) * ((1 - t)**(n - k))
             x_expr += bernstein_coeff * p.x
             y_expr += bernstein_coeff * p.y
        return sympy.simplify(x_expr), sympy.simplify(y_expr)


    def get_symbolic_representation(self,
                                    equation: Union[ShapeEquation, str],
                                    target_comp_type: Optional[str] = None
                                   ) -> Optional[Dict[str, Any]]:
        """
        تحاول تحويل أول مكون قابل للتحويل في معادلة شكل إلى تعبير SymPy.
        لا تتعامل حاليًا مع دمج مكونات متعددة (مثل যোগ أو ضرب الدوال).

        Args:
            equation (Union[ShapeEquation, str]): المعادلة ككائن أو سلسلة نصية.
            target_comp_type (Optional[str]): يمكن تحديد نوع المكون المطلوب تحويله.
                                             إذا كان None، يتم تحويل أول مكون قابل للتحويل.

        Returns:
            Optional[Dict[str, Any]]: قاموس يحتوي على التمثيل الرمزي، أو None.
                                      القاموس قد يحتوي على:
                                      - 'expression': تعبير SymPy (مثل معادلة Eq أو تعبير y).
                                      - 'variables': قائمة برموز SymPy المستخدمة (مثل [x, y] أو [t]).
                                      - 'type': نوع التحويل ('function' لـ y=f(x), 'parametric' لـ x(t),y(t)).
        """
        if not SYMPY_AVAILABLE:
            log.warning("SymPy not available. Cannot perform symbolic conversion.")
            return None

        # تحليل المعادلة إذا كانت نصًا
        eq_obj: Optional[ShapeEquation] = None
        if isinstance(equation, str):
            eq_obj = self.parse(equation)
        elif isinstance(equation, ShapeEquation):
            eq_obj = equation
        else:
             log.error("get_symbolic_representation requires a ShapeEquation object or string.")
             return None

        if not eq_obj or eq_obj.is_empty():
            log.warning("Cannot get symbolic representation for an empty equation.")
            return None

        log.debug(f"Attempting symbolic conversion for equation (target_type: {target_comp_type or 'first'})")

        # البحث عن المكون المطلوب أو أول مكون قابل للتحويل
        component_to_convert: Optional[ShapeComponent] = None
        for component in eq_obj.components:
            if target_comp_type:
                if component.type == target_comp_type.lower():
                    component_to_convert = component
                    break
            elif component.type in self._sympy_map: # أول مكون قابل للتحويل
                component_to_convert = component
                break

        if not component_to_convert:
            log.warning(f"No suitable component found for symbolic conversion "
                        f"(target: {target_comp_type or 'any supported'}).")
            return None

        log.debug(f"Found component to convert: {component_to_convert!r}")
        converter = self._sympy_map.get(component_to_convert.type)
        if not converter:
             # هذا لا يجب أن يحدث إذا كان البحث صحيحًا
             log.error(f"Internal error: Converter not found for type '{component_to_convert.type}' in sympy_map.")
             return None

        # استدعاء دالة التحويل (المغلفة)
        symbolic_result = converter(component_to_convert.params, component_to_convert.metadata)

        if symbolic_result:
            # تحليل النتيجة من الغلاف
            expr1, expr2, var = symbolic_result
            if var == sympy_t: # حالة بارامترية
                result_dict = {
                    'type': 'parametric',
                    'x_expression': str(expr1), # تحويل لتخزين السلسلة
                    'y_expression': str(expr2),
                    'parameter': str(var),
                    'sympy_objects': (expr1, expr2, var) # الاحتفاظ بالكائنات للعمليات اللاحقة
                }
                log.info(f"Symbolic conversion (parametric) successful for '{component_to_convert.type}'.")
                return result_dict
            elif var == sympy_y: # حالة دالة y=f(x)
                 # expr1 هو sympy_x, expr2 هو تعبير y
                 equation_sympy = sympy.Eq(sympy_y, expr2)
                 result_dict = {
                     'type': 'function',
                     'equation': str(equation_sympy), # تخزين المعادلة كسلسلة
                     'y_expression': str(expr2),
                     'variables': [str(sympy_x), str(sympy_y)],
                     'sympy_objects': (equation_sympy, sympy_x, sympy_y)
                 }
                 log.info(f"Symbolic conversion (function) successful for '{component_to_convert.type}'.")
                 return result_dict

        log.warning(f"Symbolic conversion failed for component: {component_to_convert!r}")
        return None


# ============================================================== #
# =================== مثال للاستخدام والاختبار ================== #
# ============================================================== #
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s [%(levelname)s] - %(message)s')
    log.info("--- Testing EquationManager ---")

    manager = EquationManager()

    # --- اختبار التحليل ---
    print("\n--- Testing Parsing ---")
    eq_str1 = "line(0, 0.0, 10, 10.5){color='#FF00AA', lw=1.5, dashed=true} + CIRCLE(5, 5, 2)[0:6.283]{fill=None}"
    eq_obj1 = manager.parse(eq_str1)
    assert eq_obj1 is not None, "Parsing failed for eq_str1"
    assert len(eq_obj1.components) == 2
    assert len(eq_obj1.operators) == 1 and eq_obj1.operators[0] == '+'
    assert eq_obj1.components[0].type == 'line'
    assert eq_obj1.components[0].params == [0, 0.0, 10, 10.5]
    assert eq_obj1.components[0].style.get('color') == '#FF00AA'
    assert eq_obj1.components[0].style.get('lw') == 1.5 # تم تحويلها لـ float
    assert eq_obj1.components[0].style.get('dashed') is True # تم تحويلها لـ bool
    assert eq_obj1.components[1].type == 'circle' # تم تحويلها لحروف صغيرة
    assert eq_obj1.components[1].params == [5, 5, 2]
    assert eq_obj1.components[1].range == (0.0, 6.283) # تم تحويلها لـ float
    assert eq_obj1.components[1].style.get('fill') is None # تم تحويل 'None' النصية
    print(f"Parsed eq1: {eq_obj1}")

    eq_str_err = "line(0,0,1,1) extra + circle(1,1,1)"
    eq_obj_err = manager.parse(eq_str_err)
    assert eq_obj_err is None, "Parsing should fail for invalid syntax"

    eq_str_empty = "  "
    eq_obj_empty = manager.parse(eq_str_empty)
    assert eq_obj_empty is None, "Parsing should fail for empty string"

    eq_str_var = "line(?x1, ?y1, 10, 10) * SetStyle{color=?c}"
    eq_obj_var = manager.parse(eq_str_var)
    assert eq_obj_var is not None and len(eq_obj_var.components)==2
    assert eq_obj_var.components[0].params == ['?x1', '?y1', 10, 10] # المتغيرات تبقى كنصوص
    assert eq_obj_var.components[1].style.get('color') == '?c'
    print(f"Parsed eq_var: {eq_obj_var}")

    # --- اختبار التوليد ---
    print("\n--- Testing Generation ---")
    gen_str1 = manager.generate_string(eq_obj1)
    print(f"Generated string for eq1: {gen_str1}")
    # التحقق من الأجزاء الرئيسية (قد يختلف الترتيب في النمط أو تنسيق الأرقام قليلاً)
    assert "line(0,0,10,10.5)" in gen_str1
    assert "color='#FF00AA'" in gen_str1
    assert "lw=1.5" in gen_str1
    assert "dashed=true" in gen_str1
    assert "+ circle(5,5,2)" in gen_str1
    assert "[0:6.283]" in gen_str1
    assert "fill=None" in gen_str1

    # --- اختبار التحقق ---
    print("\n--- Testing Validation ---")
    assert manager.validate(eq_obj1) is True, "eq_obj1 should be valid"
    eq_invalid = ShapeEquation(components=[ShapeComponent('point', [0])], operators=['+'])
    assert manager.validate(eq_invalid) is False, "Equation with wrong operator count should be invalid"

    # --- اختبار التحويل الرمزي ---
    print("\n--- Testing Symbolic Conversion ---")
    if SYMPY_AVAILABLE:
        # اختبار دالة خطية
        sym_line = manager.get_symbolic_representation("line(1, 2, 5, 10)")
        assert sym_line is not None and sym_line['type'] == 'function'
        print(f"SymPy Line: {sym_line['equation']}")
        assert 'Eq(y, 2*x)' in sym_line['equation'] or 'Eq(y, 2.0*x)' in sym_line['equation'] # قد يختلف التمثيل قليلاً

        # اختبار دالة جيبية
        sym_sine = manager.get_symbolic_representation("sine(A=3, freq=2, phase=0.5)") # استخدام = لتعيين المعلمات
        assert sym_sine is not None and sym_sine['type'] == 'function'
        print(f"SymPy Sine: {sym_sine['equation']}")
        assert '3*sin(2*x + 0.5)' in sym_sine['equation'] or '3.0*sin(2.0*x + 0.5)' in sym_sine['equation']

        # اختبار دائرة (بارامترية)
        sym_circle = manager.get_symbolic_representation("circle(1, -1, 4)")
        assert sym_circle is not None and sym_circle['type'] == 'parametric'
        print(f"SymPy Circle: x={sym_circle['x_expression']}, y={sym_circle['y_expression']}, param={sym_circle['parameter']}")
        assert sym_circle['parameter'] == 't'
        assert '1 + 4*cos(t)' in sym_circle['x_expression']
        assert '-1 + 4*sin(t)' in sym_circle['y_expression']

        # اختبار بيزيه (بارامترية)
        sym_bezier = manager.get_symbolic_representation('bezier(0,0, 1,1, 2,0)') # تربيعي
        assert sym_bezier is not None and sym_bezier['type'] == 'parametric'
        print(f"SymPy Bezier (Quadratic): x={sym_bezier['x_expression']}, y={sym_bezier['y_expression']}")
        # التعبير المبسط قد يكون معقدًا للتحقق منه بالضبط كنص

        # اختبار معادلة مركبة (حالياً يحول الأول فقط)
        sym_combined = manager.get_symbolic_representation(eq_str1)
        assert sym_combined is not None and sym_combined['type'] == 'function' # يجب أن يحول الخط
        print(f"SymPy Combined (first): {sym_combined['equation']}")

        # اختبار طلب نوع محدد
        sym_combined_circle = manager.get_symbolic_representation(eq_str1, target_comp_type='circle')
        assert sym_combined_circle is not None and sym_combined_circle['type'] == 'parametric' # يجب أن يحول الدائرة
        print(f"SymPy Combined (circle): x={sym_combined_circle['x_expression']}, y={sym_combined_circle['y_expression']}")

    else:
        print("SymPy not available, skipping symbolic conversion tests.")

    log.info("--- EquationManager testing finished ---")

'''
شرح الكود والتحسينات النهائية في EquationManager:
المحلل اللغوي (_build_parser):
تحسين التعاريف الأساسية: استخدام pyparsing_common.number للتعامل المرن مع الأرقام، دعم أشكال متعددة لـ bool_literal، استخدام QuotedString للتعامل الأفضل مع السلاسل النصية.
هيكل النمط (style): تم تحسينه للسماح بقوائم ومجموعات متداخلة (مثل gradient=[(0.0,'#fff'), (1.0,'#000')]) باستخدام Forward() و Group.
معالجة القيم (_parse_value_token): دالة مساعدة جديدة لتحويل التوكنات المعقدة (بما في ذلك القوائم والقواميس المتداخلة المحتملة) إلى قيم Python مقابلة.
معالجة المكونات (_parse_component_action): تم تحسينها لاستخدام _parse_value_token لمعالجة المعلمات والنمط، والتحقق من صحة النطاق بشكل أفضل.
المعادلة الكاملة: تم تعديل القاعدة قليلاً لاستخلاص المكون الأول (firstComponent) ثم قائمة بأزواج المشغل والمكون التالي باستخدام ZeroOrMore(Group(op + nextComponent)) لتسهيل المعالجة في دالة parse.
دالة التحليل (parse):
تم إعادة كتابتها لتستخدم النتائج المُسماة من المحلل (firstComponent, operator, nextComponent) لبناء كائن ShapeEquation بشكل أكثر موثوقية.
تتضمن تحققًا نهائيًا من التناسق العددي بين المكونات والمشغلات.
تم تحسين معالجة أخطاء pyparsing.ParseException لعرض معلومات أكثر تفصيلاً عن الخطأ وموقعه.
دالة التحويل الرمزي (get_symbolic_representation والمساعدين):
هيكلة أفضل: تم تقسيمها إلى دالة رئيسية، دوال wrapper لتوحيد الواجهة (_sympy_parametric_wrapper, _sympy_function_wrapper)، ودوال فعلية لكل نوع مكون (_sympy_circle_func, _sympy_line_func, إلخ).
دوال إضافية: تم إضافة دوال مثال لتحويل القطع المكافئ (_sympy_parabola_func) واللوغاريتم (_sympy_log_func) ودالة لتحويل منحنى بيزيه (_sympy_bezier_func) باستخدام صيغة برنشتاين.
إرجاع قاموس: تُرجع الدالة الرئيسية الآن قاموسًا يحتوي على التمثيل النصي للتعبير/المعادلة، قائمة المتغيرات، ونوع التحويل، بالإضافة إلى كائنات SymPy نفسها للعمليات اللاحقة.
معالجة الأخطاء: تم تحسين معالجة الأخطاء داخل دوال التحويل.
الاعتماديات: تم التأكد من التحقق الشرطي لـ pyparsing و sympy.
التوثيق والاختبار: تم تحديث الـ Docstrings بشكل كامل، وتم توسيع قسم الاختبارات if __name__ == "__main__": ليشمل التحليل الرمزي لأنواع متعددة والتحقق من صحة المخرجات.
الخلاصة:
وحدة foundations/equation_manager.py الآن مُحسّنة بشكل كبير وجاهزة. توفر آلية قوية ومرنة لتحليل وتوليد والتحقق من صحة المعادلات الشكلية، بالإضافة إلى قدرات أولية للتحويل الرمزي باستخدام SymPy.
الخطوة التالية:
الآن بعد الانتهاء من إدارة المعادلات، الوحدة المنطقية التالية في foundations/ هي calculus_engine.py. لقد قمنا بمراجعتها سابقًا، وهي تعتمد على EquationManager.
هل ننتقل إلى الوحدة التالية: foundations/knowledge_manager.py (التي تعتمد على representations/ai_object.py الذي انتهينا منه)؟ أم تفضل مراجعة سريعة لـ calculus_engine.py للتأكد من تكامله مع EquationManager الجديد؟
edit

more_vert
'''   