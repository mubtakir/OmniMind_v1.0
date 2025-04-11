
'''
ممتاز، لننتقل الآن إلى كتابة الكود الكامل للملف الأخير والمحوري في وحدة representations/: وهو ai_object.py.
هذا الملف سيعرّف الفئة AIObject، التي تمثل الكيان المركزي الموحد في نظام OmniMind. ستربط هذه الفئة بين التمثيل الرياضي/الهيكلي الجوهري (المُمثل بـ ShapeEquation) وبين جميع المعلومات السياقية واللغوية والمعرفية الأخرى المرتبطة به، مما يُجسد مفهوم AI_OOP بشكل كامل.
سنعتمد على التصميم الغني الذي ناقشناه سابقًا، مع التأكد من تضمين جميع السمات الهامة وتوثيقها بشكل واضح، بالإضافة إلى الدوال المساعدة الضرورية لإدارة هذه السمات.
'''

# OmniMind_v1.0/representations/ai_object.py

# -*- coding: utf-8 -*-
"""
===============================================================================
الوحدة: الكائن الكوني (AI Object) - OmniMind v1.0
===============================================================================

**الملف:** `ai_object.py`

**الموقع:** `representations/ai_object.py`

**الوصف:**
تعرف هذه الوحدة الفئة المحورية `AIObject` باستخدام `dataclasses`. يمثل
`AIObject` أي مفهوم، كيان، نمط، أو عملية في النظام المعرفي OmniMind.
تُعتبر هذه الفئة هي حجر الزاوية لتجسيد مفهوم AI_OOP، حيث تربط التمثيل
الرياضي/الهيكلي الجوهري للكائن (المُمثل بواسطة `ShapeEquation`) مع مجموعة
غنية من السمات والمعلومات الأخرى، بما في ذلك:
-   المعرفات الفريدة (instance ID و canonical name المستمد من المعادلة).
-   التمثيلات اللغوية متعددة اللغات.
-   الخصائص الديناميكية والمستخلصة.
-   الروابط المعرفية مع الكائنات الأخرى.
-   البيانات الوصفية (المصدر، الثقة، الزمن، إلخ).

**الفئات المعرفة:**
-   `AIObject`: فئة بيانات لتخزين جميع المعلومات المتعلقة بكيان معرفي واحد.

**الاعتماديات:**
-   `dataclasses`, `field`: لتسهيل تعريف الفئة والتحكم في سماتها.
-   `typing`: لتحديد الأنواع بوضوح (List, Dict, Any, Optional, Set, Tuple).
-   `logging`: لتسجيل المعلومات والتحذيرات الهامة.
-   `uuid`: لتوليد معرفات فريدة عالميًا للمثيلات (instance ID).
-   `time`: للحصول على الطوابع الزمنية وإدارتها.
-   `.shape_equation`: لاستخدام فئة `ShapeEquation` وحساب التوقيع الأساسي.

**المساهمة في النظام:**
-   توفر التمثيل الموحد والشامل لجميع الكيانات والمفاهيم داخل النظام.
-   تربط بشكل صريح بين التمثيل الرياضي/الهيكلي والمعلومات اللغوية والسياقية والمعرفية.
-   تعمل كوحدة أساسية يتم تخزينها، فهرستها، ومعالجتها بواسطة جميع الوحدات
    الأخرى في النظام (مثل `KnowledgeManager`, `CognitiveModules`, `OmniMindEngine`).
-   تمكن من بناء قاعدة معرفة غنية ومترابطة وقابلة للاستدلال.
-   تسمح بتتبع مصدر وثقة وتطور المعرفة المرتبطة بكل كائن عبر البيانات الوصفية.
"""

import uuid
import time
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set, Tuple

# استيراد ShapeEquation للتحقق من النوع ولحساب التوقيع
try:
    from .shape_equation import ShapeEquation
except ImportError:
    # حل بديل في حالة تشغيل الملف مباشرة للاختبار
    from shape_equation import ShapeEquation

# إعداد المسجل (Logger)
log = logging.getLogger(__name__)

# ============================================================== #
# =================== DATA CLASS: AIObject =================== #
# ============================================================== #

# eq=False: المساواة الفعلية بين مثيلات AIObject تعتمد فقط على instance_id الفريد.
# unsafe_hash=True: يسمح بتعريف دالة __hash__ الخاصة بنا المعتمدة على instance_id.
@dataclass(eq=False, unsafe_hash=True)
class AIObject:
    """
    الكائن الأساسي الموحد في نظام OmniMind AI_OOP. يمثل أي مفهوم أو كيان،
    يُعرَّف بشكل أساسي بواسطة معادلته الشكلية (`ShapeEquation`) الفريدة كهوية
    منطقية، ومعرف مثيل (`instance_id`) فريد كهوية وجودية في الذاكرة.

    Attributes:
        instance_id (str): معرّف فريد عالمي للمثيل (UUID v4). لا يتغير وهو أساس
                           الهوية الوجودية للكائن. يُنشأ تلقائيًا.
        equation (ShapeEquation): الوصف الرياضي/الهيكلي للشكل أو المفهوم.
                                  هذا هو التعريف الجوهري والمنطقي للكائن.
                                  يمكن أن تتغير هذه المعادلة إذا تطور فهم النظام
                                  للكائن، مما قد يؤدي لتغير `canonical_name`.
        canonical_name (Optional[str]): الاسم الأساسي الحتمي المشتق من تجزئة
                                         المعادلة الشكلية (`equation.get_canonical_signature()`).
                                         يُستخدم كمعرف ثابت نسبيًا للهيكل المنطقي
                                         للكائن، وهو مفيد جدًا للربط والفهرسة
                                         في المعجم اللغوي (`LinguisticLexicon`)
                                         والبحث عن كائنات ذات بنية مماثلة. يتغير
                                         تلقائيًا عند تغير `equation`.
        linguistic_tags (Dict[str, str]): قاموس يربط هذا الكائن بأسمائه المقروءة
                                         بواسطة البشر في لغات مختلفة. المفتاح هو
                                         رمز اللغة (مثل 'ar', 'en') والقيمة هي
                                         الاسم المقابل. تتم إدارتها بواسطة
                                         `KnowledgeManager` بالتعاون مع `LinguisticLexicon`.
        properties (Dict[str, Any]): قاموس لتخزين الخصائص الديناميكية، المستخلصة،
                                     أو القابلة للتغيير للكائن (مثل اللون المحسوب،
                                     الحجم المقدر، الحالة الحالية 'نائم'، متجه السمات
                                     المستخلص، السمات المتعلمة من `PatternEngine`).
                                     المفاتيح هي أسماء الخصائص والقيم هي قيمها.
        knowledge_links (List[Dict[str, Any]]): قائمة بالروابط الصادرة من هذا الكائن
                                                 إلى كائنات أخرى في الرسم البياني المعرفي.
                                                 كل رابط هو قاموس يمثل علاقة منطقية أو
                                                 هيكلية أو سببية، ويحتوي على الأقل على:
                                                 - 'relation' (str): اسم الفعل المنطقي للعلاقة.
                                                 - 'target_id' (str): معرف `instance_id` للكائن الهدف.
                                                 ويمكن أن يحتوي على خصائص إضافية للرابط
                                                 (مثل 'confidence', 'source', 'timestamp', 'weight').
                                                 تتم إدارتها بواسطة `KnowledgeManager`.
        recognition_confidence (float): درجة الثقة (بين 0.0 و 1.0) إذا كان هذا الكائن
                                       قد تم إنشاؤه أو التعرف عليه بواسطة عملية
                                       غير مؤكدة (مثل كشف الكائنات في الصور أو
                                       استخلاص المعلومات من نص غامض). الافتراضي 1.0.
        metadata (Dict[str, Any]): قاموس مرن لتخزين البيانات الوصفية الإضافية
                                   التي لا تندرج تحت التصنيفات الأخرى، مثل:
                                   - 'created_at' (float): الطابع الزمني لإنشاء المثيل (Unix timestamp).
                                   - 'last_updated_at' (float): الطابع الزمني لآخر تحديث مهم للمعادلة أو الخصائص.
                                   - 'source' (str): مصدر المعلومات أو العملية التي أدت لإنشاء/تحديث الكائن
                                     (مثل معرف ملف، اسم وحدة معرفية، "UserInput").
                                   - 'tags' (Set[str]): مجموعة من العلامات أو الكلمات المفتاحية العامة المرتبطة بالكائن.
                                   - 'external_ids' (Dict[str, str]): قاموس للمعرفات في قواعد بيانات خارجية (مثل {'wikidata': 'Q146'}).
                                   - 'aliases' (Set[str]): مجموعة من الأسماء أو الألقاب البديلة الأخرى (بالإضافة إلى `linguistic_tags`).
    """

    # --- السمات الأساسية والمعرفات ---
    # instance_id: يتم إنشاؤه تلقائيًا ولا يجب تعيينه مباشرة عند الإنشاء.
    # repr=False: لا يتم تضمينه في التمثيل النصي الافتراضي لـ dataclass.
    instance_id: str = field(default_factory=lambda: str(uuid.uuid4()), init=False, repr=False, compare=False)
    # المعادلة الشكلية هي جوهر الكائن المنطقي.
    equation: ShapeEquation = field(default_factory=ShapeEquation, compare=False)
    # الاسم الأساسي: يعتمد على المعادلة، يتم حسابه في __post_init__، ولا يشارك في المقارنة الافتراضية.
    canonical_name: Optional[str] = field(init=False, default=None, compare=False)

    # --- السمات اللغوية والمعرفية ---
    linguistic_tags: Dict[str, str] = field(default_factory=dict, compare=False)
    properties: Dict[str, Any] = field(default_factory=dict, compare=False)
    knowledge_links: List[Dict[str, Any]] = field(default_factory=list, compare=False)

    # --- سمات الحالة والتعرف ---
    recognition_confidence: float = field(default=1.0, compare=False)

    # --- البيانات الوصفية ---
    metadata: Dict[str, Any] = field(default_factory=dict, compare=False)

    # --- الطابع الزمني (للسهولة، نضعه كسمة مباشرة، لكنه مُدار في metadata) ---
    timestamp: float = field(init=False, default=0.0, compare=False)


    def __post_init__(self):
        """
        تُنفذ بعد الإنشاء الأولي.
        - تتحقق من صحة الأنواع الأساسية.
        - تُهيئ حقول البيانات الوصفية الأساسية (الطوابع الزمنية، المصدر، إلخ).
        - تحسب الاسم الأساسي (`canonical_name`) الأولي بناءً على المعادلة.
        - تضيف الأسماء اللغوية الأولية إلى الأسماء البديلة.
        """
        now = time.time()
        # التحقق من نوع المعادلة
        if not isinstance(self.equation, ShapeEquation):
            raise TypeError("AIObject attribute 'equation' must be a ShapeEquation instance.")
        if not isinstance(self.linguistic_tags, dict): raise TypeError("AIObject 'linguistic_tags' must be a dict.")
        if not isinstance(self.properties, dict): raise TypeError("AIObject 'properties' must be a dict.")
        if not isinstance(self.knowledge_links, list): raise TypeError("AIObject 'knowledge_links' must be a list.")
        if not isinstance(self.metadata, dict): raise TypeError("AIObject 'metadata' must be a dict.")
        if not isinstance(self.recognition_confidence, (int, float)): raise TypeError("AIObject 'recognition_confidence' must be numeric.")

        # تهيئة البيانات الوصفية الأساسية إذا لم تكن موجودة
        self.metadata.setdefault('created_at', now)
        self.metadata.setdefault('last_updated_at', self.metadata['created_at'])
        self.metadata.setdefault('source', 'unknown')
        self.metadata.setdefault('tags', set())
        self.metadata.setdefault('external_ids', {})
        self.metadata.setdefault('aliases', set())

        # تعيين الطابع الزمني الرئيسي (عادة آخر تحديث)
        self.timestamp = self.metadata['last_updated_at']
        # ضمان أن الثقة ضمن النطاق الصحيح
        self.recognition_confidence = max(0.0, min(1.0, float(self.recognition_confidence)))

        # حساب الاسم الأساسي الأولي
        self._update_canonical_name()

        # إضافة الأسماء اللغوية الأولية إلى الأسماء البديلة
        for name in self.linguistic_tags.values():
            if name and isinstance(name, str):
                self.metadata['aliases'].add(name.strip())
        # إضافة الاسم الأساسي كاسم بديل أيضًا (للتوحيد)
        if self.canonical_name:
             self.metadata['aliases'].add(self.canonical_name)

        log.debug(f"AIObject initialized: ID={self.instance_id[:8]}, CanonName={self.canonical_name}")

    def _update_timestamp(self):
        """(داخلي) تحديث الطابع الزمني لآخر تعديل."""
        now = time.time()
        self.metadata['last_updated_at'] = now
        self.timestamp = now

    def _update_canonical_name(self):
        """
        (داخلي) يحسب أو يعيد حساب الاسم الأساسي (`canonical_name`) بناءً على
        التوقيع الحتمي للمعادلة الشكلية الحالية (`equation`).
        يتم استدعاؤها عند التهيئة وعند تغيير المعادلة.
        """
        old_name = self.canonical_name
        if self.equation and not self.equation.is_empty():
            # استخدام التوقيع الأساسي (بدون النمط) للمعادلة
            signature = self.equation.get_canonical_signature(include_style=False)
            # الاسم الأساسي هو بادئة ثابتة + جزء من التجزئة لضمان التفرد والقراءة
            self.canonical_name = f"shape_{signature[:16]}" # استخدام أول 16 حرفًا (يمكن تعديل الطول)
        else:
            # اسم مؤقت ومميز إذا كانت المعادلة فارغة أو غير موجودة
            self.canonical_name = f"~empty_{self.instance_id[:8]}" # استخدام ~ للتمييز

        # إضافة الاسم الأساسي الجديد كمستعار وتحديث الوقت إذا تغير الاسم
        if old_name != self.canonical_name:
            if self.canonical_name:
                self.metadata['aliases'].add(self.canonical_name)
            # تغيير الاسم الأساسي يعتبر تحديثًا مهمًا
            self._update_timestamp()
            log.debug(f"Canonical name for ID {self.instance_id[:8]} updated: {old_name} -> {self.canonical_name}")

    # --- دوال تعديل الكائن ---

    def set_equation(self, new_equation: ShapeEquation, update_confidence: Optional[float] = None):
        """
        تحديث المعادلة الشكلية للكائن.
        تقوم بإعادة حساب الاسم الأساسي تلقائيًا وتحديث الطابع الزمني.

        Args:
            new_equation (ShapeEquation): المعادلة الشكلية الجديدة.
            update_confidence (Optional[float]): يمكن تحديث درجة الثقة اختياريًا
                                                 أثناء تغيير المعادلة.
        """
        if not isinstance(new_equation, ShapeEquation):
            raise TypeError("Input must be a ShapeEquation instance.")

        # التحقق إذا تغيرت المعادلة منطقيًا لتجنب التحديث غير الضروري
        if new_equation.get_canonical_signature() != self.equation.get_canonical_signature():
            log.info(f"Updating equation for AIObject {self.instance_id[:8]}...")
            self.equation = new_equation
            self._update_canonical_name() # الاسم الأساسي سيتغير ويتسبب في تحديث الطابع الزمني
            if update_confidence is not None:
                 self.recognition_confidence = max(0.0, min(1.0, float(update_confidence)))
                 log.debug(f"  Confidence updated to {self.recognition_confidence:.2f}")
        elif update_confidence is not None and self.recognition_confidence != update_confidence:
             # تحديث الثقة فقط إذا لم تتغير المعادلة
             self.recognition_confidence = max(0.0, min(1.0, float(update_confidence)))
             self._update_timestamp() # يعتبر تحديث الثقة مهمًا
             log.debug(f"  Confidence updated to {self.recognition_confidence:.2f} (equation unchanged).")
        else:
             log.debug(f"  set_equation called with identical equation for {self.instance_id[:8]}. No update.")

    def update_property(self, key: str, value: Any, source: Optional[str] = None):
        """
        تحديث أو إضافة خاصية ديناميكية للكائن.
        تقوم بتحديث الطابع الزمني فقط إذا تغيرت قيمة الخاصية.

        Args:
            key (str): اسم الخاصية (سيتم إزالة المسافات).
            value (Any): القيمة الجديدة للخاصية.
            source (Optional[str]): مصدر هذا التحديث (لتحديث بيانات المصدر للكائن).
        """
        clean_key = key.strip()
        if not clean_key:
            log.warning(f"Attempted to update property with empty key for {self.instance_id[:8]}.")
            return

        if self.properties.get(clean_key) != value:
            # log.debug(f"Updating property '{clean_key}' for {self.instance_id[:8]}: '{self.properties.get(clean_key)}' -> '{value}'")
            self.properties[clean_key] = value
            # تحديث مصدر الكائن بأكمله إذا تم توفير مصدر جديد
            if source:
                self.metadata['source'] = source
            self._update_timestamp() # تم تغيير الخاصية، نحدث الطابع الزمني

    def get_property(self, key: str, default: Any = None) -> Any:
        """الحصول على قيمة خاصية مع قيمة افتراضية."""
        return self.properties.get(key.strip(), default)

    def add_linguistic_tag(self, lang: str, name: str):
        """
        إضافة أو تحديث اسم الكائن بلغة معينة في `linguistic_tags`.
        تقوم أيضًا بإضافة الاسم الجديد إلى الأسماء البديلة (`aliases`) في `metadata`.
        لا تقوم بتحديث الطابع الزمني الرئيسي افتراضيًا.

        Args:
            lang (str): رمز اللغة (مثل 'ar', 'en').
            name (str): الاسم المقابل باللغة المحددة.
        """
        lang_code = lang.strip().lower()
        clean_name = name.strip()
        if lang_code and clean_name:
            if self.linguistic_tags.get(lang_code) != clean_name:
                 log.debug(f"Adding/Updating linguistic tag for {self.canonical_name or self.instance_id[:8]}: {lang_code}='{clean_name}'")
                 self.linguistic_tags[lang_code] = clean_name
                 # إضافة الاسم كمستعار تلقائيًا
                 self.metadata['aliases'].add(clean_name)
                 # لا نحدث الطابع الزمني الرئيسي هنا
        else:
            log.warning(f"Attempted to add empty language ('{lang}') or name ('{name}') tag.")

    def get_linguistic_name(self, lang: str,
                            default_to_english: bool = True,
                            default_to_canonical: bool = True) -> Optional[str]:
        """
        الحصول على اسم الكائن المقروء باللغة المطلوبة.

        Args:
            lang (str): رمز اللغة المطلوبة (مثل 'ar').
            default_to_english (bool): إذا لم يوجد الاسم باللغة المطلوبة، هل يتم
                                      الرجوع إلى اللغة الإنجليزية ('en')؟
            default_to_canonical (bool): إذا لم يتم العثور على اسم لغوي، هل يتم
                                       إرجاع الاسم الأساسي (`canonical_name`)؟

        Returns:
            Optional[str]: الاسم باللغة المطلوبة، أو اسم احتياطي، أو `canonical_name`،
                           أو None إذا لم يتم العثور على أي اسم مناسب.
        """
        lang_code = lang.strip().lower()
        name = self.linguistic_tags.get(lang_code)
        if name: return name

        if default_to_english and lang_code != 'en':
            name_en = self.linguistic_tags.get('en')
            if name_en: return name_en

        if default_to_canonical:
            # الاسم الأساسي قد يكون None إذا كانت المعادلة فارغة ولم يتم تعيين اسم
            return self.canonical_name
        else:
            # إذا لم نرغب في إرجاع الاسم الأساسي، ولم نجد أي اسم لغوي
             return None # أو يمكن إرجاع معرف مؤقت مثل "unnamed_{self.instance_id[:4]}"

    def add_tag(self, tag: str):
        """إضافة علامة أو كلمة مفتاحية عامة للكائن."""
        clean_tag = tag.strip()
        if clean_tag:
            self.metadata.setdefault('tags', set()).add(clean_tag)

    def add_alias(self, alias: str):
        """إضافة اسم بديل (Alias) للكائن."""
        clean_alias = alias.strip()
        if clean_alias and clean_alias != self.canonical_name and clean_alias not in self.linguistic_tags.values():
            added = self.metadata.setdefault('aliases', set()).add(clean_alias)
            # لا نحدث الطابع الزمني لإضافة اسم مستعار

    def add_external_id(self, source_db: str, external_id: str):
        """إضافة معرف من قاعدة بيانات خارجية."""
        if source_db and external_id:
            db_key = source_db.strip().lower()
            ext_id_clean = external_id.strip()
            if self.metadata.setdefault('external_ids', {}).get(db_key) != ext_id_clean:
                 log.debug(f"Adding external ID for {self.instance_id[:8]}: {db_key}='{ext_id_clean}'")
                 self.metadata['external_ids'][db_key] = ext_id_clean
                 self._update_timestamp() # يعتبر تحديثًا مهمًا

    def add_knowledge_link(self, relation: str, target_id: str, check_duplicates: bool = True, **kwargs):
        """
        إضافة رابط معرفي صادر من هذا الكائن إلى كائن آخر (بواسطة معرفه).

        Args:
            relation (str): اسم الفعل المنطقي للعلاقة.
            target_id (str): معرف `instance_id` للكائن الهدف.
            check_duplicates (bool): هل يجب التحقق من وجود رابط مطابق تمامًا
                                     (نفس العلاقة ونفس الهدف) قبل الإضافة؟ الافتراضي True.
            **kwargs: خصائص إضافية للرابط (مثل 'confidence', 'source', 'weight').
                      سيتم إضافة 'timestamp' تلقائيًا.
        """
        clean_relation = relation.strip()
        clean_target_id = target_id.strip()
        if not clean_relation or not clean_target_id:
             log.warning(f"Cannot add knowledge link with empty relation ('{relation}') or target_id ('{target_id}') for {self.instance_id[:8]}.")
             return

        # التحقق من التكرار إذا طلب
        if check_duplicates:
            link_exists = any(
                lk.get('relation') == clean_relation and lk.get('target_id') == clean_target_id
                for lk in self.knowledge_links
            )
            if link_exists:
                # log.debug(f"Link '{clean_relation}' to {clean_target_id[:8]} already exists for {self.instance_id[:8]}. Skipping add.")
                return # لا تقم بالإضافة

        # إنشاء قاموس بيانات الرابط
        link_data = {
            'relation': clean_relation,
            'target_id': clean_target_id,
            'timestamp': time.time(), # إضافة طابع زمني لإنشاء الرابط
            **kwargs # دمج أي خصائص إضافية تم تمريرها
        }
        self.knowledge_links.append(link_data)
        # log.debug(f"Added link from {self.instance_id[:8]} -> '{clean_relation}' -> {clean_target_id[:8]} with data: {kwargs}")
        # إضافة رابط لا يعتبر تحديثًا جوهريًا للكائن نفسه (لا يستدعي _update_timestamp)

    def get_links(self, relation_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """الحصول على الروابط الصادرة (يمكن ترشيحها حسب نوع العلاقة)."""
        if relation_type:
            clean_relation_type = relation_type.strip()
            return [link for link in self.knowledge_links if link.get('relation') == clean_relation_type]
        else:
            # إرجاع نسخة من القائمة لمنع التعديل الخارجي المباشر
            return list(self.knowledge_links)

    # --- دوال الهوية والمقارنة ---

    def __hash__(self):
        """الهاش يعتمد فقط وحصرًا على `instance_id` الفريد عالميًا."""
        return hash(self.instance_id)

    def __eq__(self, other: object) -> bool:
        """
        المساواة بين مثيلات `AIObject` تعتمد فقط وحصرًا على تطابق
        `instance_id` الفريد عالميًا. كائنان يعتبران نفس المثيل فقط
        إذا كان لهما نفس `instance_id`.
        """
        if not isinstance(other, AIObject):
            return NotImplemented
        return self.instance_id == other.instance_id

    def has_same_core_logic(self, other: 'AIObject') -> bool:
        """
        (دالة مقارنة إضافية) تتحقق مما إذا كان كائن آخر يمثل نفس
        الشكل أو المفهوم المنطقي الأساسي، بناءً على تطابق
        `canonical_name` (المشتق من `ShapeEquation`).

        Args:
            other (AIObject): الكائن الآخر للمقارنة.

        Returns:
            bool: True إذا كان للكائنين نفس الاسم الأساسي، False خلاف ذلك.
        """
        if not isinstance(other, AIObject):
            return False
        # المقارنة بناءً على الاسم الأساسي (الذي يعكس المعادلة الأساسية)
        # يجب التأكد من أن الأسماء الأساسية ليست None
        return self.canonical_name is not None and self.canonical_name == other.canonical_name

    # --- التمثيل النصي ---

    def __repr__(self) -> str:
        """تمثيل نصي مفصل للمطورين يتضمن أهم السمات."""
        # محاولة الحصول على اسم عربي أو إنجليزي أو الاسم الأساسي
        display_name = self.get_linguistic_name('ar', default_to_english=True, default_to_canonical=True)
        if display_name == self.canonical_name:
             name_part = f"Canon='{self.canonical_name}'"
        elif display_name:
             name_part = f"Name='{display_name}' (Canon='{self.canonical_name}')"
        else: # حالة عدم وجود أي اسم
             name_part = f"Canon='{self.canonical_name}'"


        # اختصار لبعض السمات للعرض
        props_count = len(self.properties)
        links_count = len(self.knowledge_links)
        eq_len = len(self.equation) if self.equation else 0

        return (f"AIObject(ID='{self.instance_id[:8]}...', " # عرض جزء من ID
                f"{name_part}, "
                f"Props={props_count}, Links={links_count}, EqLen={eq_len}, "
                f"Conf={self.recognition_confidence:.2f})")


log.info("Module representations/ai_object.py loaded successfully: AIObject defined.")
# --- نهاية ملف ai_object.py ---

'''
شرح الكود والتحسينات في AIObject (v1.0):
السمات الأساسية:
instance_id: يستخدم uuid.uuid4() لضمان التفرد العالمي، init=False, repr=False.
equation: من نوع ShapeEquation، هو الجوهر المنطقي.
canonical_name: يُحسب تلقائيًا في __post_init__ و set_equation باستخدام equation.get_canonical_signature(). يُستخدم كمعرف للهيكل المنطقي.
السمات اللغوية والمعرفية: linguistic_tags, properties, knowledge_links كما تم تعريفها سابقًا.
البيانات الوصفية (metadata): قاموس مرن لتخزين معلومات إضافية. تم توحيد الطوابع الزمنية (created_at, last_updated_at) داخل metadata، مع إضافة سمة timestamp كاختصار لـ last_updated_at لسهولة الوصول والفرز. تم التأكد من تهيئة الحقول الأساسية (tags, external_ids, aliases) في __post_init__.
__post_init__:
يقوم بتهيئة الطوابع الزمنية في metadata.
يستدعي _update_canonical_name() لحساب الاسم الأساسي.
يضيف الأسماء اللغوية الأولية إلى aliases.
يتحقق من أنواع السمات الرئيسية.
_update_canonical_name(): تُحسب الاسم بناءً على تجزئة المعادلة الأساسية (بدون النمط) وتُضيفه إلى aliases وتُحدّث الطابع الزمني إذا تغير الاسم.
set_equation(): تتحقق مما إذا كانت المعادلة الجديدة مختلفة منطقيًا (باستخدام التوقيع) قبل إجراء التحديث، وتُحدّث الاسم الأساسي والطابع الزمني عند التغيير.
update_property(): تُحدّث الطابع الزمني فقط إذا تغيرت قيمة الخاصية.
add_linguistic_tag(): تضيف الوسم اللغوي وتُضيفه تلقائيًا للأسماء البديلة. لا تُحدّث الطابع الزمني الرئيسي.
get_linguistic_name(): توفر خيارات مرنة للرجوع إلى لغات أخرى أو الاسم الأساسي.
add_alias(), add_external_id(), add_tag(): دوال مساعدة لإدارة حقول metadata المقابلة. add_external_id تُحدّث الطابع الزمني.
add_knowledge_link(): تضيف رابطًا إلى knowledge_links مع طابع زمني خاص بالرابط، وخيار للتحقق من التكرار.
__eq__() و __hash__(): الأهم: تعتمد الآن فقط وحصرًا على instance_id الفريد عالميًا. هذا يعني أن كل مثيل AIObject تم إنشاؤه هو فريد بحد ذاته ويمكن استخدامه بأمان كمفتاح في القواميس أو في المجموعات داخل KnowledgeManager أو الوحدات الأخرى. المقارنة المنطقية بين كائنين (هل يمثلان نفس المفهوم؟) تتم الآن باستخدام has_same_core_logic().
has_same_core_logic(): دالة جديدة للمقارنة المنطقية بناءً على تطابق canonical_name.
__repr__(): تم تحسينها لعرض معلومات أكثر فائدة وتناسقًا، بما في ذلك الاسم بأكثر من لغة (إن وجد) أو الاسم الأساسي، وعدد الخصائص والروابط وطول المعادلة.
الخلاصة لوحدة representations:
بهذا الملف، اكتملت وحدة representations/ بشكل تام. لقد قمنا بتعريف هياكل البيانات الجوهرية الثلاثة (ShapeComponent, ShapeEquation, AIObject) التي تشكل أساس تمثيل المعرفة في نظام OmniMind v1.0. هذه الهياكل مترابطة وتجسد مفهوم AI_OOP الذي يربط التمثيل الرياضي/الهيكلي بالمعلومات اللغوية والمعرفية والسياقية.
الخطوة التالية:
الآن بعد الانتهاء من وحدة representations الأساسية، يمكننا الانتقال إلى الوحدات التي تعالج وتستخدم هذه الهياكل. بناءً على اقتراحك السابق، سننتقل إلى أول وحدة في foundations/: وهي foundations/equation_manager.py. هذه الوحدة ستكون مسؤولة عن تحليل وتوليد ومعالجة كائنات ShapeEquation.
هل أنت جاهز للبدء في foundations/equation_manager.py؟
'''