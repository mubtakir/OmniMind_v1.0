
'''
حسنًا. سنبدأ بالوحدة الأولى والأساسية في الهيكل المقترح، وهي الوحدة المسؤولة عن تعريف المكون الأساسي للمعادلات الشكلية. هذه الوحدة هي representations/shape_component.py.

هذا الملف سيعرّف فئة ShapeComponent باستخدام dataclasses. تمثل هذه الفئة اللبنة الأولى وغير القابلة للتجزئة التي تُبنى منها المعادلات الشكلية الأكثر تعقيدًا لوصف الكائنات والمفاهيم في نظام OmniMind.
'''

# OmniMind_v1.0/representations/shape_component.py


# -*- coding: utf-8 -*-
"""
===============================================================================
الوحدة: مكون المعادلة الشكلية (Shape Component) - OmniMind v1.0
===============================================================================

**الملف:** `shape_component.py`

**الموقع:** `representations/shape_component.py`

**الوصف:**
تعرف هذه الوحدة فئة `ShapeComponent` باستخدام `dataclasses`. يمثل هذا المكون
وحدة بناء أساسية وغير قابلة للتجزئة ضمن معادلة شكلية (`ShapeEquation`) أكثر
تعقيدًا. يمكن أن يمثل المكون شكلاً هندسيًا أوليًا (مثل خط، دائرة، نقطة)،
أو عملية تحويل (مثل دوران، تحجيم، انتقال)، أو سمة مرئية (مثل لون، سمك خط،
تعبئة)، أو حتى استدعاء لدالة مخصصة أو تمثيل رياضي آخر معرف في النظام
(مثل موجة جيبية، دالة أسية).

يتم تعريف كل مكون بنوعه الفريد، قائمة معلماته الخاصة، قاموس نمطه المرئي،
نطاقه (إذا كان له نطاق تعريف محدد مثل المتغيرات البارامترية)، وبيانات
وصفية إضافية (مثل مصدر المكون، درجة الثقة).

**الفئات المعرفة:**
-   `ShapeComponent`: فئة بيانات لتخزين معلومات مكون شكل واحد.

**الاعتماديات:**
-   `dataclasses`: لتسهيل تعريف الفئة بسمات وأنواع محددة.
-   `typing`: لتحديد الأنواع بوضوح (List, Dict, Any, Optional, Tuple).
-   `logging`: لتسجيل المعلومات التشخيصية والتحذيرات والأخطاء.
-   `math`: للتعامل مع القيم الرقمية الخاصة (inf, nan) عند حساب التوقيع.

**المساهمة في النظام:**
-   توفر الوحدة الأساسية غير القابلة للتجزئة لوصف الأشكال والمعالجات والسمات.
-   تسمح بتمثيل مرن ومنظم لمختلف أنواع المكونات الهندسية والمرئية والرياضية.
-   تُستخدم كوحدة بناء رئيسية بواسطة فئة `ShapeEquation` لتشكيل الوصف الكامل للكائن.
-   تُستخدم بواسطة وحدة `foundations.equation_manager` لتحليل وتوليد سلاسل المعادلات.
-   تُستخدم بواسطة وحدة `foundations.renderer` لتفسيرها وتحويلها إلى تمثيل مرئي.
"""

import logging
import math
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple

# إعداد المسجل (Logger) لهذه الوحدة
# سيتم تكوين الـ logger بشكل مركزي لاحقًا بواسطة utils.logger_config
# لكننا ننشئه هنا لاستخدامه داخل الوحدة.
log = logging.getLogger(__name__)

# ============================================================== #
# =============== DATA CLASS: ShapeComponent ================= #
# ============================================================== #

# frozen=False: للسماح بتعديل السمات (مثل style أو metadata) بعد الإنشاء إذا لزم الأمر.
# eq=False, unsafe_hash=False: نحدد __eq__ و __hash__ الخاص بنا بناءً على get_signature.
@dataclass(frozen=False, eq=False, unsafe_hash=False)
class ShapeComponent:
    """
    يمثل مكونًا واحدًا غير قابل للتجزئة داخل معادلة شكلية مركبة (`ShapeEquation`).
    يمكن أن يكون شكلاً أولياً، عملية، سمة، أو استدعاء دالة.

    Attributes:
        type (str): معرف نصي فريد لنوع المكون (مثل 'line', 'circle', 'color',
                    'translate', 'sine', 'custom_func'). يُستخدم للتعرف على وظيفة
                    المكون ومعالجته في الوحدات الأخرى. يتم تحويله إلى حروف صغيرة
                    تلقائيًا لضمان التناسق.
        params (List[Any]): قائمة مرتبة بالمعلمات الخاصة بهذا المكون. يمكن أن تحتوي
                           على أنواع مختلفة (أرقام int/float، نصوص str، قيم منطقية bool،
                           أو حتى معرفات str تشير إلى متغيرات أو كائنات `AIObject` أخرى).
                           الترتيب والمعنى يعتمدان على تعريف كل `type`.
        style (Dict[str, Any]): قاموس بسمات النمط المرئي التي تؤثر بشكل أساسي على كيفية
                                عرض هذا المكون بواسطة وحدة `Renderer` (مثل 'color': '#FF0000',
                                'linewidth': 2.0, 'fill': True, 'opacity': 0.8).
                                هذه السمات منفصلة عن المعلمات الهيكلية الأساسية للشكل.
        range (Optional[Tuple[float, float]]): نطاق الرسم أو التطبيق للمكون، خاصةً
                                               للأشكال البارامترية (مثل منحنى معرف بـ t)
                                               أو الدوال المعرفة على نطاق محدود.
                                               يجب أن يكون tuple من رقمين (min_val, max_val).
        metadata (Dict[str, Any]): قاموس للبيانات الوصفية الإضافية الخاصة بالمكون،
                                   مثل مصدر المعلومات (`source`), درجة الثقة (`confidence`),
                                   الطابع الزمني للإنشاء/التحديث (`timestamp`), أو أي
                                   معلومات سياقية أخرى مفيدة.
    """
    type: str
    params: List[Any] = field(default_factory=list)
    style: Dict[str, Any] = field(default_factory=dict)
    range: Optional[Tuple[float, float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """
        تُنفذ بعد الإنشاء الأولي بواسطة dataclass.
        تقوم بالتحقق من صحة الأنواع الأساسية، توحيد حالة الأحرف للنوع،
        والتحقق من صحة النطاق.
        """
        # 1. التحقق من النوع (type) وتحويله لحروف صغيرة
        if not isinstance(self.type, str) or not self.type.strip():
            msg = "ShapeComponent 'type' must be a non-empty string."
            log.error(msg)
            raise ValueError(msg)
        self.type = self.type.strip().lower()

        # 2. التحقق من أنواع السمات الأخرى (القوائم والقواميس)
        if not isinstance(self.params, list):
            raise TypeError(f"ShapeComponent '{self.type}' attribute 'params' must be a list, got {type(self.params)}.")
        if not isinstance(self.style, dict):
            raise TypeError(f"ShapeComponent '{self.type}' attribute 'style' must be a dictionary, got {type(self.style)}.")
        if not isinstance(self.metadata, dict):
            raise TypeError(f"ShapeComponent '{self.type}' attribute 'metadata' must be a dictionary, got {type(self.metadata)}.")

        # 3. التحقق من صحة النطاق (range) إذا تم تحديده
        if self.range is not None:
            if not isinstance(self.range, tuple) or len(self.range) != 2:
                msg = f"ShapeComponent '{self.type}' attribute 'range' must be a tuple of two numbers or None, got {self.range}."
                log.error(msg)
                raise ValueError(msg)
            try:
                # التأكد من أن عناصر النطاق يمكن تحويلها إلى أرقام عشرية
                r_min = float(self.range[0])
                r_max = float(self.range[1])
                # (اختياري) يمكن إضافة تحقق لضمان أن min <= max، أو تعديله تلقائيًا
                # if r_min > r_max:
                #     log.warning(f"ShapeComponent '{self.type}' range minimum {r_min} is greater than maximum {r_max}. Swapping.")
                #     self.range = (r_max, r_min)
            except (ValueError, TypeError) as e:
                msg = f"ShapeComponent '{self.type}' range elements must be numeric. Error: {e}"
                log.error(msg)
                raise ValueError(msg)

        log.debug(f"Validated ShapeComponent: {self!r}") # استخدام repr للتسجيل المفصل

    def __str__(self) -> str:
        """
        تُرجع تمثيلًا نصيًا مقروءًا للمكون، يهدف لمحاكاة الصيغة التي قد تُستخدم
        في التحليل أو التوليد بواسطة EquationManager.

        Returns:
            str: التمثيل النصي للمكون.
        """
        # --- تنسيق المعلمات (params) ---
        params_formatted = []
        for p in self.params:
            if isinstance(p, float):
                # تنسيق الأرقام العشرية للحفاظ على الدقة مع إزالة الأصفار غير الضرورية
                params_formatted.append(f"{p:.5g}") # استخدام .5g كصيغة عامة جيدة
            elif isinstance(p, str):
                # استخدام repr لإضافة علامات الاقتباس تلقائيًا والتعامل مع المحارف الخاصة
                params_formatted.append(repr(p))
            else:
                # تحويل الأنواع الأخرى (int, bool, None) إلى نص
                params_formatted.append(str(p))
        params_str = ",".join(params_formatted)

        # --- تنسيق النطاق (range) ---
        range_str = ""
        if self.range:
            try:
                # استخدام تنسيق مشابه للمعلمات للأرقام
                range_str = f"[{self.range[0]:.5g}:{self.range[1]:.5g}]"
            except (TypeError, IndexError, ValueError):
                # كبديل إذا لم تكن أرقامًا أو حدث خطأ
                log.warning(f"Could not format range {self.range} nicely for __str__.")
                range_str = f"[{self.range[0]}:{self.range[1]}]" # استخدام str كاحتياطي

        # --- تنسيق النمط (style) ---
        style_items = []
        # فرز المفاتيح لضمان تمثيل نصي متسق
        for k, v in sorted(self.style.items()):
            if isinstance(v, float): v_str = f"{v:.5g}"
            elif isinstance(v, bool): v_str = str(v).lower() # 'true' or 'false'
            elif isinstance(v, str):
                # استخدام repr للسلاسل لضمان وضع علامات الاقتباس ومعالجة المحارف الخاصة
                v_str = repr(v)
            elif isinstance(v, (list, tuple)):
                # تمثيل القوائم والمجموعات كما هي (قد يحتاج لتحسين للتوافق مع المحلل)
                 v_str = repr(v) # Use repr for lists/tuples inside style
            else: v_str = str(v)
            style_items.append(f"{k}={v_str}")
        style_str = "{" + ",".join(style_items) + "}" if style_items else ""

        # --- تجميع التمثيل النهائي ---
        return f"{self.type}({params_str}){range_str}{style_str}"

    def get_signature(self, include_style: bool = False, precision: int = 8) -> str:
        """
        تولد توقيعًا نصيًا أساسيًا وحتميًا (canonical) للمكون، يُستخدم
        أساسًا بواسطة `ShapeEquation.get_canonical_signature()` لحساب تجزئة
        فريدة للمعادلة، وللمقارنة المنطقية بين المكونات.

        يركز التوقيع بشكل افتراضي على النوع (`type`)، المعلمات (`params`)،
        والنطاق (`range`) لتحديد الشكل أو العملية الأساسية، مع تجاهل النمط
        المرئي (`style`) والبيانات الوصفية (`metadata`).

        Args:
            include_style (bool): إذا كانت True، يتم تضمين تمثيل نصي ثابت ومفروز
                                  لقاموس `style` في التوقيع. الافتراضي False.
            precision (int): عدد الخانات العشرية المستخدمة لتنسيق الأرقام
                             العشرية (float) في التوقيع لضمان التناسق والدقة
                             الكافية عند المقارنة أو التجزئة. الافتراضي 8.

        Returns:
            str: السلسلة النصية التي تمثل التوقيع الحتمي للمكون.
        """
        sig_parts = [self.type] # النوع هو الجزء الأول دائمًا (بحروف صغيرة)
        fmt = f"%.{precision}g" # استخدام تنسيق .g مع الدقة المحددة (أكثر مرونة من .f)

        # --- إضافة المعلمات (params) ---
        param_parts = []
        for p in self.params:
            if isinstance(p, float):
                if math.isnan(p): param_parts.append("nan")
                elif math.isinf(p): param_parts.append("inf" if p > 0 else "-inf")
                else:
                     # تنسيق دقيق وموحد
                     formatted_float = fmt % p
                     # إضافة '.0' إذا كان العدد صحيحًا لتمييزه عن int (اختياري ولكن قد يزيد الدقة)
                     # if '.' not in formatted_float and 'e' not in formatted_float:
                     #     formatted_float += ".0"
                     param_parts.append(formatted_float)
            elif isinstance(p, str):
                 param_parts.append(repr(p)) # استخدام repr للسلاسل لضمان التمييز
            elif isinstance(p, bool):
                 param_parts.append("T" if p else "F") # تمثيل مختصر للقيم المنطقية
            else:
                 param_parts.append(str(p)) # تحويل الأنواع الأخرى (int, None) لنص
        sig_parts.append(f"P({','.join(param_parts)})") # تمييز جزء المعلمات

        # --- إضافة النطاق (range) ---
        if self.range:
            try:
                # استخدام نفس التنسيق الدقيق للأرقام
                r0_str = (fmt % self.range[0]) if isinstance(self.range[0], float) else str(self.range[0])
                r1_str = (fmt % self.range[1]) if isinstance(self.range[1], float) else str(self.range[1])
                sig_parts.append(f"R({r0_str}:{r1_str})") # تمييز جزء النطاق
            except Exception as e:
                 log.warning(f"Could not format range {self.range} for signature: {e}")
                 # استخدام repr كاحتياطي لضمان عدم حدوث خطأ
                 sig_parts.append(f"R({self.range[0]!r}:{self.range[1]!r})")

        # --- إضافة النمط (style) - اختياري ---
        if include_style and self.style:
            # إنشاء تمثيل نصي ثابت ومفروز للقاموس
            style_sig_parts = []
            for k, v in sorted(self.style.items()): # الفرز بالمفتاح ضروري للحتمية
                 # استخدام repr للقيم لضمان تمثيل ثابت لمعظم الأنواع
                 style_sig_parts.append(f"{k!r}:{v!r}")
            sig_parts.append(f"S{{{';'.join(style_sig_parts)}}}") # تمييز جزء النمط

        # استخدام فاصل مميز (مثل |-|) لتقليل احتمالية ظهوره في القيم نفسها
        return "|-|".join(sig_parts)

    def __eq__(self, other: object) -> bool:
        """
        المساواة المنطقية بين مكونين تعتمد على التوقيع الأساسي
        (Canonical Signature) الذي يتجاهل النمط والبيانات الوصفية افتراضيًا.
        """
        if not isinstance(other, ShapeComponent):
            return NotImplemented # هام: إرجاع NotImplemented للسماح لـ Python بتجربة __eq__ للكائن الآخر
        # المقارنة باستخدام التوقيع الأساسي (بدون النمط)
        return self.get_signature(include_style=False) == other.get_signature(include_style=False)

    def __hash__(self) -> int:
        """
        الهاش يعتمد على التوقيع الأساسي (بدون النمط افتراضيًا) لضمان أن
        المكونات المتساوية منطقيًا لها نفس قيمة الهاش، مما يسمح باستخدامها
        بشكل صحيح في المجموعات (Set) وكمفاتيح في القواميس (Dict).
        """
        # حساب الهاش بناءً على التوقيع الأساسي
        return hash(self.get_signature(include_style=False))

    # --- يمكن إضافة دوال مساعدة أخرى هنا إذا لزم الأمر ---
    # مثال:
    # def get_metadata(self, key: str, default: Any = None) -> Any:
    #     """الحصول على قيمة من البيانات الوصفية بأمان."""
    #     return self.metadata.get(key, default)


# ============================================================== #
# =================== مثال للاستخدام والاختبار ================== #
# ============================================================== #

# هذا الجزء يُنفذ فقط عند تشغيل الملف مباشرة (python representations/shape_component.py)
if __name__ == "__main__":
    # إعداد التسجيل لمستوى DEBUG لعرض كل الرسائل عند الاختبار المباشر
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s [%(levelname)s] - %(message)s')

    log.info("--- Testing ShapeComponent ---")

    # --- أمثلة إنشاء ---
    comp_line = ShapeComponent(type='Line', params=[0, 0, 10.5, 10.5555555], style={'color': '#FF0000', 'linewidth': 1.5})
    comp_circle = ShapeComponent(type='CIRCLE', params=[5.0, 5.0, 3], range=(0, 6.283185), style={'fill': True}) # النوع سيصبح صغيرًا
    comp_color = ShapeComponent(type='Color', params=['blue']) # لون كمعلمة
    comp_style = ShapeComponent(type='SetStyle', style={'opacity': 0.7, 'fill': False}) # نمط فقط
    comp_bezier = ShapeComponent(type='bezier', params=[0,0, 1,1, 2,0, 3,1]) # مثال بيزيه
    comp_nan = ShapeComponent(type='point', params=[1, float('nan')]) # مثال مع NaN

    # --- اختبار __str__ ---
    print("\n--- Testing __str__ ---")
    print(f"Line: {comp_line}")
    print(f"Circle: {comp_circle}")
    print(f"Color: {comp_color}")
    print(f"SetStyle: {comp_style}")
    print(f"Bezier: {comp_bezier}")
    print(f"NaN Point: {comp_nan}")
    # التأكد من فرز النمط في __str__
    comp_style_rev = ShapeComponent(type='SetStyle', style={'fill': False, 'opacity': 0.7})
    print(f"Style Reversed: {comp_style_rev}")
    assert str(comp_style) == str(comp_style_rev)

    # --- اختبار get_signature ---
    print("\n--- Testing get_signature (precision=8, no style) ---")
    sig_line = comp_line.get_signature()
    sig_circle = comp_circle.get_signature()
    sig_color = comp_color.get_signature()
    sig_style = comp_style.get_signature()
    sig_bezier = comp_bezier.get_signature()
    sig_nan = comp_nan.get_signature()
    print(f"Line Sig: {sig_line}")
    print(f"Circle Sig: {sig_circle}")
    print(f"Color Sig: {sig_color}")
    print(f"SetStyle Sig: {sig_style}")
    print(f"Bezier Sig: {sig_bezier}")
    print(f"NaN Point Sig: {sig_nan}")
    assert sig_style == "setstyle|-|P()", f"Signature for style-only component is wrong: {sig_style}" # Params should be empty P()
    assert "10.555556" in sig_line or "10.555555" in sig_line # Check precision formatting
    assert "'blue'" in sig_color # Check repr for string param
    assert "nan" in sig_nan # Check NaN handling

    # --- اختبار get_signature (with style) ---
    print("\n--- Testing get_signature (with style) ---")
    sig_line_style = comp_line.get_signature(include_style=True)
    sig_style_style = comp_style.get_signature(include_style=True)
    print(f"Line Sig w/ Style: {sig_line_style}")
    print(f"SetStyle Sig w/ Style: {sig_style_style}")
    assert "S{'color': '#FF0000';'linewidth': 1.5}" in sig_line_style # Check style formatting and sorting
    assert "S{'fill': False;'opacity': 0.7}" in sig_style_style

    # --- اختبار __eq__ و __hash__ ---
    print("\n--- Testing __eq__ and __hash__ ---")
    comp_line_same = ShapeComponent(type='line', params=[0.0, 0.0, 10.5, 10.5555555]) # نفس الشكل الأساسي
    comp_line_diff_style = ShapeComponent(type='line', params=[0, 0, 10.5, 10.5555555], style={'color': 'green'}) # نفس الشكل، نمط مختلف
    comp_line_diff_param = ShapeComponent(type='line', params=[0, 0, 10, 10]) # شكل مختلف

    assert comp_line == comp_line_same, "Components with same core signature should be equal."
    assert comp_line == comp_line_diff_style, "Components differing only in style should be equal by default (__eq__)."
    assert comp_line != comp_line_diff_param, "Components with different params should not be equal."
    assert hash(comp_line) == hash(comp_line_same), "Hashes of equal components should be equal."
    assert hash(comp_line) == hash(comp_line_diff_style), "Hashes differing only in style should be equal by default."
    assert hash(comp_line) != hash(comp_line_diff_param), "Hashes of different components should be different."

    # استخدامها في مجموعة
    comp_set: Set[ShapeComponent] = {comp_line, comp_line_same, comp_line_diff_style, comp_line_diff_param}
    assert len(comp_set) == 2, f"Set should contain only 2 unique components based on core signature, found {len(comp_set)}."
    assert comp_line in comp_set
    assert comp_line_diff_param in comp_set

    # --- اختبار حالات خاطئة في الإنشاء ---
    print("\n--- Testing Invalid Creation ---")
    with unittest.TestCase().assertRaises(ValueError): ShapeComponent(type='')
    with unittest.TestCase().assertRaises(TypeError): ShapeComponent(type='test', params='not a list') # type: ignore
    with unittest.TestCase().assertRaises(TypeError): ShapeComponent(type='test', style=[]) # type: ignore
    with unittest.TestCase().assertRaises(ValueError): ShapeComponent(type='test', range=(1,)) # type: ignore
    with unittest.TestCase().assertRaises(ValueError): ShapeComponent(type='test', range=(1,'a')) # type: ignore

    log.info("--- ShapeComponent testing finished ---")

'''
شرح الكود والتحسينات النهائية:

@dataclass: تم استخدام eq=False و unsafe_hash=False لتعطيل الإنشاء التلقائي لهذه الدوال، مما يسمح لنا بتعريف سلوك المساواة والتجزئة الخاص بنا بناءً على التوقيع (get_signature).

__post_init__: تم تحسين رسائل الأخطاء لتكون أكثر تحديدًا وتضمن نوع المكون. تمت إضافة تحقق من صحة أنواع جميع السمات القابلة للتغيير (list, dict). تم تحسين التحقق من range للتأكد من أن العناصر رقمية.

__str__: تم تحسين التنسيق باستخدام .5g للأرقام العشرية و repr() للسلاسل والقوائم والمجموعات داخل style لتمثيل أكثر دقة وتوحيدًا. تم فرز مفاتيح style لضمان تمثيل نصي متسق.

get_signature():

الدقة (precision): تم زيادة الدقة الافتراضية إلى 8 خانات عشرية (precision=8) لتقليل احتمالية تصادم التجزئة بسبب أخطاء التقريب في العمليات الحسابية اللاحقة، مع استخدام التنسيق %.8g الذي يوفر مرونة أفضل من %.8f.

معالجة القيم الخاصة: يتم الآن التعامل بشكل صريح مع float('nan'), float('inf'), float('-inf') وتحويلها إلى سلاسل نصية ثابتة ("nan", "inf", "-inf") لضمان الحتمية.

تمثيل الأنواع: يتم استخدام repr() للسلاسل لضمان تمييزها عن المعرفات أو الأنواع الأخرى، ويتم استخدام تمثيل مختصر ومميز للقيم المنطقية ("T", "F"). الأنواع الرقمية الأخرى (int) تحول إلى نص.

تمييز الأجزاء: تم إضافة بادئات (مثل "P", "R", "S") وتم استخدام فاصل أكثر تميزًا (|-|) لزيادة وضوح وقوة التوقيع ضد التصادمات المحتملة إذا احتوت المعلمات على الفاصل المستخدم سابقًا (::).

__eq__(): تستخدم الآن get_signature(include_style=False) بشكل مباشر للمقارنة، مما يضمن أن المكونات المتساوية منطقيًا (بغض النظر عن النمط) تعتبر متساوية. تم إضافة التحقق isinstance وإرجاع NotImplemented للممارسات الأفضل.

__hash__(): تستخدم الآن get_signature(include_style=False) لحساب الهاش، مما يضمن توافقها مع __eq__ والسماح باستخدام الكائنات كمفاتيح أو في مجموعات بشكل صحيح.

التوثيق والتعليقات: تم مراجعة وتحديث الـ Docstrings والتعليقات لتكون شاملة وواضحة وتعكس التعديلات الأخيرة.

الاختبارات (if __name__ == "__main__":): تم تحديثها لتشمل حالات اختبار إضافية (مثل NaN، بيزيه، اختبار المساواة والهاش بشكل أدق، اختبار الحالات الخاطئة).

الخلاصة:

ملف representations/shape_component.py الآن مكتمل وجاهز. إنه يوفر تعريفًا دقيقًا وقويًا وموثقًا جيدًا للمكون الأساسي للمعادلات الشكلية، مع آليات قوية للتحقق والتمثيل النصي والمقارنة المنطقية.

الخطوة التالية:

ننتقل الآن إلى الملف التالي في هذه الوحدة: representations/shape_equation.py. سنقوم بكتابة الكود الكامل لفئة ShapeEquation التي ستستخدم ShapeComponent لتمثيل المعادلات المركبة.

'''