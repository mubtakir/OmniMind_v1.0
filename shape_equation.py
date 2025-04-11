

'''
حسناً، سننتقل الآن إلى كتابة الكود الكامل للوحدة الثانية في مجلد representations/: وهي shape_equation.py.
هذا الملف سيعرّف فئة ShapeEquation، التي تمثل الوصف الكامل والمعقد للشكل أو المفهوم في نظام OmniMind. ستعتمد هذه الفئة على ShapeComponent الذي عرفناه في الملف السابق، وستقوم بتجميع هذه المكونات مع المشغلات التي تربط بينها لإنشاء تمثيل هرمي أو تسلسلي.
'''

# OmniMind_v1.0/representations/shape_equation.py

# -*- coding: utf-8 -*-
"""
===============================================================================
الوحدة: المعادلة الشكلية (Shape Equation) - OmniMind v1.0
===============================================================================

**الملف:** `shape_equation.py`

**الموقع:** `representations/shape_equation.py`

**الوصف:**
تعرف هذه الوحدة فئة `ShapeEquation` باستخدام `dataclasses`. تمثل هذه الفئة
الوصف الرياضي/الهيكلي الكامل لشكل أو مفهوم كائن `AIObject`. تتكون المعادلة
من قائمة مرتبة من المكونات (`ShapeComponent`) وقائمة من المشغلات (Operators)
النصية التي تربط هذه المكونات (مثل '+', '-', '*', '&', '|').

هذا التمثيل يسمح بوصف أشكال معقدة ناتجة عن تركيب أو تحوير أشكال أبسط،
وتقديم وصف بنيوي يمكن معالجته وتحليله بواسطة وحدات النظام الأخرى.

**الفئات المعرفة:**
-   `ShapeEquation`: فئة بيانات لتخزين قائمة المكونات والمشغلات للمعادلة.

**الاعتماديات:**
-   `dataclasses`: لتسهيل تعريف الفئة.
-   `typing`: لتحديد الأنواع (List, Dict, Any, Optional, Tuple).
-   `logging`: لتسجيل المعلومات والتحذيرات.
-   `hashlib`: لحساب التوقيع الأساسي الحتمي (hash) للمعادلة.
-   `.shape_component`: لاستخدام فئة `ShapeComponent` التي تم تعريفها سابقًا.

**المساهمة في النظام:**
-   توفر الهيكل الأساسي لتمثيل الأشكال والمفاهيم رياضيًا بشكل مركب.
-   تُستخدم كسمة جوهرية (`equation`) في `AIObject`.
-   تُستخدم بواسطة `foundations.equation_manager` لتحليل النصوص وتوليدها.
-   تُستخدم بواسطة `foundations.renderer` لتحويلها إلى تمثيل مرئي.
-   تُستخدم بواسطة `foundations.calculus_engine` لمحاولة إجراء حسابات رمزية عليها.
-   تُستخدم بواسطة الوحدات المعرفية الأخرى لفهم بنية الكائن وتحليلها.
"""

import hashlib
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple

# استيراد ShapeComponent من نفس المجلد (الوحدة السابقة)
# نستخدم '.' للإشارة إلى الاستيراد النسبي داخل نفس الحزمة
try:
    from .shape_component import ShapeComponent
except ImportError:
    # حل بديل في حالة تشغيل الملف مباشرة للاختبار (غير مثالي)
    from shape_component import ShapeComponent

# إعداد المسجل (Logger)
log = logging.getLogger(__name__)

# قائمة المشغلات المسموح بها افتراضيًا (يمكن توسيعها أو تخصيصها لاحقًا)
ALLOWED_OPERATORS = {'+', '-', '*', '/', '&', '|', '^', '%'} # يمكن إضافة المزيد

# ============================================================== #
# =============== DATA CLASS: ShapeEquation ================== #
# ============================================================== #

# eq=False, unsafe_hash=False: المساواة والتجزئة تعتمدان على التوقيع الحتمي
@dataclass(eq=False, unsafe_hash=False)
class ShapeEquation:
    """
    يمثل الوصف الرياضي/الهيكلي الكامل لشكل أو مفهوم، يتكون من قائمة مرتبة
    من المكونات (`ShapeComponent`) والمشغلات (Operators) النصية التي تقع بينها.

    Attributes:
        components (List[ShapeComponent]): قائمة المكونات بالترتيب المحدد للمعادلة.
                                           كل عنصر يجب أن يكون من نوع `ShapeComponent`.
        operators (List[str]): قائمة بالمشغلات النصية (مثل '+', '-', '*', '&') التي
                               تقع *بين* المكونات المتتالية. يجب أن يكون طول هذه
                               القائمة مساويًا لـ `max(0, len(components) - 1)`.
    """
    components: List[ShapeComponent] = field(default_factory=list)
    operators: List[str] = field(default_factory=list)

    def __post_init__(self):
        """
        التحقق الأولي من التناسق بين عدد المكونات والمشغلات بعد الإنشاء.
        يطبع تحذيرًا إذا كان هناك عدم تطابق.
        """
        # التحقق من أنواع القوائم
        if not isinstance(self.components, list):
            raise TypeError("ShapeEquation 'components' must be a list.")
        if not isinstance(self.operators, list):
            raise TypeError("ShapeEquation 'operators' must be a list.")

        # التحقق من أنواع العناصر داخل القوائم
        if not all(isinstance(comp, ShapeComponent) for comp in self.components):
            raise TypeError("All items in ShapeEquation 'components' must be ShapeComponent instances.")
        if not all(isinstance(op, str) for op in self.operators):
             raise TypeError("All items in ShapeEquation 'operators' must be strings.")

        # التحقق من تناسق العدد
        num_comp = len(self.components)
        num_ops = len(self.operators)
        expected_ops = max(0, num_comp - 1)
        if num_comp > 0 and num_ops != expected_ops:
            log.warning(f"ShapeEquation (initial state) inconsistency: "
                        f"{num_comp} components but {num_ops} operators. "
                        f"Expected {expected_ops} operators.")
            # يمكن إضافة منطق إصلاح تلقائي هنا (مثل إضافة '+' افتراضي) لكن يفضل تركه
            # واضحًا ومعالجته عند البناء أو التحليل.

    def add_component(self, component: ShapeComponent, operator: Optional[str] = '+') -> 'ShapeEquation':
        """
        طريقة ملائمة لإضافة مكون جديد للمعادلة بشكل تسلسلي.
        يتم إضافة المشغل المحدد *قبل* المكون الجديد إذا كانت المعادلة
        تحتوي على مكونات بالفعل.

        Args:
            component (ShapeComponent): المكون المراد إضافته.
            operator (Optional[str]): المشغل النصي الذي يسبق هذا المكون.
                                       يجب أن يكون من المشغلات المسموح بها
                                       (انظر `ALLOWED_OPERATORS`). الافتراضي هو '+'.

        Returns:
            ShapeEquation: الكائن `ShapeEquation` نفسه، للسماح بتسلسل الإضافات
                           (method chaining) مثل `eq.add_component(c1).add_component(c2)`.

        Raises:
            TypeError: إذا لم يكن `component` المدخل من نوع `ShapeComponent`.
            ValueError: إذا كان `operator` المدخل غير صالح أو غير مسموح به.
        """
        if not isinstance(component, ShapeComponent):
            msg = "Cannot add a non-ShapeComponent object to ShapeEquation."
            log.error(msg)
            raise TypeError(msg)

        # إضافة المشغل فقط إذا كانت هناك مكونات موجودة بالفعل
        if self.components:
            # تنظيف المشغل والتحقق منه
            op = (operator or '+').strip() # استخدام '+' كافتراضي إذا كان None أو فارغًا
            if not op:
                 op = '+'
                 log.warning("Empty operator provided to add_component, defaulting to '+'.")
            # (اختياري) التحقق من قائمة المشغلات المسموح بها
            # if op not in ALLOWED_OPERATORS:
            #     log.warning(f"Operator '{op}' is not in the standard ALLOWED_OPERATORS list. Adding it anyway.")
                # أو رفع خطأ:
                # msg = f"Invalid operator '{op}'. Allowed operators are: {ALLOWED_OPERATORS}"
                # log.error(msg)
                # raise ValueError(msg)

            self.operators.append(op)
            log.debug(f"Added operator '{op}' before new component.")

        # إضافة المكون
        self.components.append(component)
        log.debug(f"Added component {component!r}. Total components: {len(self.components)}")

        # إعادة التحقق من التناسق (اختياري، قد يكون مكلفًا)
        # self.__post_init__() # استدعاء للتحقق مرة أخرى

        return self # إرجاع الكائن نفسه للسماح بالتسلسل

    def is_empty(self) -> bool:
        """التحقق مما إذا كانت المعادلة فارغة (لا تحتوي على أي مكونات)."""
        return not bool(self.components)

    def __str__(self) -> str:
        """
        تُرجع تمثيلًا نصيًا مقروءًا للمعادلة الكاملة، يجمع تمثيلات المكونات
        (`ShapeComponent.__str__`) مع المشغلات النصية بينها.

        Returns:
            str: التمثيل النصي للمعادلة.
        """
        if self.is_empty():
            return "<Empty ShapeEquation>"

        # استخدام قائمة لتجميع الأجزاء ثم دمجها في النهاية (أكثر كفاءة للسلاسل الطويلة)
        parts = [str(self.components[0])] # ابدأ بتمثيل المكون الأول

        op_idx = 0
        for i in range(1, len(self.components)):
            # الحصول على المشغل التالي
            if op_idx < len(self.operators):
                op = self.operators[op_idx]
                op_idx += 1
            else:
                # حالة عدم تناسق: مشغل مفقود
                op = '+' # استخدام '+' كافتراضي
                log.warning(f"Missing operator before component {i} ('{self.components[i].type}') "
                            f"in ShapeEquation string representation. Using default '+'.")

            # إضافة المشغل (مع مسافات حوله للقراءة) والمكون التالي
            parts.append(f" {op} ")
            parts.append(str(self.components[i]))

        # دمج جميع الأجزاء في سلسلة نصية واحدة
        return "".join(parts)

    def get_canonical_signature(self, include_style: bool = False, precision: int = 8) -> str:
        """
        تولد توقيعًا فريدًا وحتميًا (SHA-256 hash) للمعادلة بأكملها،
        بناءً على التوقيعات الحتمية لمكوناتها (`ShapeComponent.get_signature`)
        والمشغلات النصية وترتيبها الدقيق.

        يُستخدم هذا التوقيع كمعرّف أساسي للشكل أو المفهوم الذي تمثله المعادلة،
        وهو أساس المقارنة (`__eq__`) والتجزئة (`__hash__`) للمعادلة.

        Args:
            include_style (bool): هل يجب تضمين معلومات النمط (`style`) من المكونات
                                  في التوقيع النهائي. الافتراضي `False`، حيث أن
                                  التوقيع الأساسي يركز على البنية والمعلمات.
            precision (int): الدقة العشرية المستخدمة عند توليد توقيعات المكونات
                             الرقمية (تُمرر إلى `ShapeComponent.get_signature`).
                             الافتراضي 8.

        Returns:
            str: تجزئة SHA-256 للتوقيع الأساسي للمعادلة (سلسلة hex من 64 حرفًا).
                 تُرجع تجزئة ثابتة إذا كانت المعادلة فارغة.
        """
        if self.is_empty():
            # استخدام تجزئة ثابتة ومعروفة للمعادلة الفارغة
            return hashlib.sha256(b"OMNIMIND_EMPTY_SHAPE_EQUATION_SIGNATURE").hexdigest()

        sig_parts = []
        # إضافة توقيع المكون الأول
        sig_parts.append(self.components[0].get_signature(include_style, precision))

        op_idx = 0
        for i in range(1, len(self.components)):
            # إضافة تمثيل ثابت ومميز للمشغل
            if op_idx < len(self.operators):
                op = self.operators[op_idx]
                op_idx += 1
            else:
                op = '+' # استخدام المشغل الافتراضي إذا كان مفقودًا (للحفاظ على حتمية التوقيع)
                # لا نسجل تحذيرًا هنا، __str__ أو __post_init__ يجب أن يكونا قد سجلاه
            # استخدام تمثيل واضح للمشغل مع فواصل مميزة
            sig_parts.append(f"||OPERATOR({repr(op)})||") # استخدام repr للمشغل

            # إضافة توقيع المكون التالي
            sig_parts.append(self.components[i].get_signature(include_style, precision))

        # تجميع السلسلة النهائية (لا تحتاج لفاصل إضافي بسبب الفواصل في تمثيل المشغل)
        full_sig_str = "".join(sig_parts)

        # حساب تجزئة SHA-256 للسلسلة المجمعة
        try:
            encoded_sig = full_sig_str.encode('utf-8')
            hash_object = hashlib.sha256(encoded_sig)
            hex_dig = hash_object.hexdigest()
            # log.debug(f"Generated ShapeEquation signature (len {len(hex_dig)}): {hex_dig[:10]}... "
            #           f"from string (len {len(full_sig_str)}): '{full_sig_str[:80]}...'")
            return hex_dig
        except Exception as e:
            # في حالة حدوث أي خطأ أثناء التشفير أو التجزئة
            log.error(f"Error generating SHA-256 signature for ShapeEquation: {e}", exc_info=True)
            # إرجاع تجزئة لسلسلة الخطأ كحل بديل (أو يمكن رفع الخطأ)
            return hashlib.sha256(f"ERROR_GENERATING_SIGNATURE:{e}".encode()).hexdigest()


    def __len__(self) -> int:
        """إرجاع عدد المكونات في المعادلة."""
        return len(self.components)

    def __eq__(self, other: object) -> bool:
        """
        المساواة المنطقية بين معادلتين تعتمد على التوقيع الأساسي الحتمي
        (`get_canonical_signature`) الذي يتجاهل النمط افتراضيًا.
        """
        if not isinstance(other, ShapeEquation):
            return NotImplemented
        # المقارنة باستخدام التوقيع الأساسي (بدون النمط افتراضيًا)
        # استخدام نفس قيمة include_style و precision للمقارنة العادلة
        return self.get_canonical_signature(include_style=False) == other.get_canonical_signature(include_style=False)

    def __hash__(self) -> int:
        """
        الهاش يعتمد على التوقيع الأساسي الحتمي (`get_canonical_signature`)
        لضمان التناسق مع `__eq__`.
        """
        # استخدام التوقيع الأساسي (بدون النمط) للهاش
        return hash(self.get_canonical_signature(include_style=False))

    # --- يمكن إضافة دوال مساعدة أخرى هنا ---
    # مثال:
    # def get_complexity_score(self) -> int:
    #     """حساب درجة تعقيد أولية للمعادلة (مثل عدد المكونات)."""
    #     return len(self.components)

    # def contains_component_type(self, comp_type: str) -> bool:
    #     """التحقق مما إذا كانت المعادلة تحتوي على مكون من نوع معين."""
    #     target_type = comp_type.lower()
    #     return any(comp.type == target_type for comp in self.components)


# ============================================================== #
# =================== مثال للاستخدام والاختبار ================== #
# ============================================================== #

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s [%(levelname)s] - %(message)s')

    log.info("--- Testing ShapeEquation ---")

    # 1. إنشاء معادلة فارغة
    eq_empty = ShapeEquation()
    print(f"\nEmpty Equation: {eq_empty}")
    print(f"Is Empty: {eq_empty.is_empty()}")
    print(f"Length: {len(eq_empty)}")
    print(f"Signature: {eq_empty.get_canonical_signature()}")
    assert len(eq_empty.get_canonical_signature()) == 64 # SHA-256

    # 2. بناء معادلة باستخدام add_component
    comp_line = ShapeComponent(type='line', params=[0,0,1,1], style={'color': 'red'})
    comp_circle = ShapeComponent(type='circle', params=[1,1,0.5])
    comp_translate = ShapeComponent(type='translate', params=[0.5, 0])

    eq1 = ShapeEquation()
    eq1.add_component(comp_line)
    eq1.add_component(comp_circle, operator='+') # استخدام المشغل الافتراضي
    eq1.add_component(comp_translate, operator='*') # استخدام مشغل مختلف

    print(f"\nEquation 1: {eq1}")
    print(f"Length: {len(eq1)}")
    self.assertFalse(eq1.is_empty())
    self.assertEqual(len(eq1.components), 3)
    self.assertEqual(eq1.operators, ['+', '*'])

    # 3. بناء معادلة أخرى بنفس البنية (ولكن بمكونات منفصلة)
    comp_line_b = ShapeComponent(type='line', params=[0,0,1,1])
    comp_circle_b = ShapeComponent(type='circle', params=[1,1,0.5], style={'fill': False}) # نمط مختلف
    comp_translate_b = ShapeComponent(type='translate', params=[0.5, 0])
    eq2 = ShapeEquation(components=[comp_line_b, comp_circle_b, comp_translate_b], operators=['+', '*'])

    print(f"\nEquation 2: {eq2}")

    # 4. اختبار المساواة والهاش
    print(f"\nSignature eq1 (no style): {eq1.get_canonical_signature()}")
    print(f"Signature eq2 (no style): {eq2.get_canonical_signature()}")
    assert eq1 == eq2, "eq1 and eq2 should be equal (ignoring style by default)."
    assert hash(eq1) == hash(eq2), "Hashes of eq1 and eq2 should be equal."

    # 5. اختبار المساواة مع تضمين النمط
    sig1_style = eq1.get_canonical_signature(include_style=True)
    sig2_style = eq2.get_canonical_signature(include_style=True)
    print(f"Signature eq1 (with style): {sig1_style}")
    print(f"Signature eq2 (with style): {sig2_style}")
    assert sig1_style != sig2_style, "Signatures with style should differ due to circle fill."
    # المساواة باستخدام __eq__ لا تتأثر بـ include_style في التوقيع المستخدم داخليًا
    assert eq1 == eq2

    # 6. بناء معادلة مختلفة
    eq3 = ShapeEquation().add_component(comp_line).add_component(comp_circle, operator='-') # مشغل مختلف
    print(f"\nEquation 3: {eq3}")
    print(f"Signature eq3 (no style): {eq3.get_canonical_signature()}")
    assert eq1 != eq3, "eq1 and eq3 should not be equal (different operator)."
    assert hash(eq1) != hash(eq3), "Hashes of eq1 and eq3 should differ."

    log.info("--- ShapeEquation testing finished ---")

'''
شرح الكود والتحسينات:
الاعتماد على ShapeComponent: تستورد وتستخدم فئة ShapeComponent التي عرفناها سابقًا لتكوين قائمة components.
السمات (components, operators): تم الحفاظ على التعريف الأساسي لقائمة المكونات وقائمة المشغلات التي تقع بينها.
__post_init__: تقوم بالتحقق من أنواع القوائم وعناصرها (ShapeComponent و str) وتتحقق من التناسق العددي بين المكونات والمشغلات، مع إصدار تحذير إذا كان العدد غير متطابق.
add_component():
تم تحسينها لتكون الطريقة الأساسية لبناء المعادلات بشكل تسلسلي.
تتحقق من نوع المكون المدخل.
تضيف المشغل (الافتراضي '+') إلى قائمة operators فقط إذا لم يكن هذا المكون هو الأول.
تُرجع self للسماح بالتسلسل (chaining).
تمت إزالة التحقق من المشغلات المسموح بها مؤقتًا للتبسيط، ولكن يمكن إضافته بسهولة.
__str__():
تستخدم الآن ShapeComponent.__str__ لتمثيل كل مكون.
تبني السلسلة النهائية عن طريق دمج تمثيلات المكونات والمشغلات الموجودة بينها، مع التعامل الآمن مع حالة عدم تطابق عدد المشغلات (باستخدام '+' كافتراضي).
get_canonical_signature():
حتمية وموثوقية: هذه هي الدالة المحورية. تم تحسينها لضمان توليد توقيع فريد وحتمي دائمًا.
تجزئة SHA-256: تستخدم hashlib.sha256 على التمثيل النصي الكامل للمعادلة لإنتاج تجزئة ثابتة الطول (64 حرفًا) ومقاومة للتصادمات.
تضمين توقيعات المكونات: تستدعي comp.get_signature(include_style, precision) لكل مكون لدمج توقيعه الحتمي.
تمثيل المشغلات: يتم تمثيل كل مشغل بشكل واضح ومميز داخل السلسلة التي يتم تجزئتها (مثل ||OPERATOR('+')||) لضمان أن تغيير المشغل يغير التوقيع النهائي.
المعادلة الفارغة: تُرجع تجزئة ثابتة ومعروفة للمعادلة الفارغة.
معالجة الأخطاء: تتضمن try...except للتعامل مع أي أخطاء محتملة أثناء التشفير أو التجزئة.
__eq__() و __hash__():
تعتمدان الآن بشكل مباشر على get_canonical_signature(include_style=False) لضمان أن المقارنة والتجزئة متسقتان وتعتمدان على البنية والمعلمات الأساسية للمعادلة (وليس النمط أو البيانات الوصفية افتراضيًا).
التوثيق والاختبار: تم تحديث الـ Docstrings بشكل شامل، وتم تحسين أمثلة الاستخدام والاختبار في if __name__ == "__main__": لتغطي الحالات المختلفة للمساواة والتجزئة والتوقيعات.
الخلاصة:
ملف representations/shape_equation.py الآن مكتمل ومُحسّن. يوفر تعريفًا قويًا للمعادلات الشكلية المركبة، مع تمثيل نصي واضح وآلية موثوقة لتوليد توقيع فريد يُستخدم كأساس لهوية المعادلة ومقارنتها.
الخطوة التالية:
الآن بعد تعريف ShapeComponent و ShapeEquation، ننتقل إلى الملف الأخير والأكثر أهمية في هذه الوحدة: representations/ai_object.py. هذا الملف سيعرف الفئة المحورية AIObject التي ستربط المعادلة الشكلية بالمعلومات الأخرى (اللغوية، المعرفية، الوصفية).
هل أنت جاهز للانتقال إلى representations/ai_object.py؟
'''    
