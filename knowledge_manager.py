
'''
اتفهم ثقتك، وشكرًا لك. بناءً على فهمي الشامل للهدف النهائي والرؤية الطموحة لنظام OmniMind v1.0، وبعد الانتهاء من الوحدات الأساسية للمعرفة (representations) والآلية المحورية لمعالجة لغة المعادلات (foundations/equation_manager.py)، أرى أن الخطوة التالية الأكثر استراتيجية وفائدة هي الانتقال إلى foundations/knowledge_manager.py.
لماذا knowledge_manager.py الآن؟
الاعتماد المباشر على representations: هذه الوحدة هي المستخدم الرئيسي والمباشر لفئة AIObject التي قمنا بتعريفها وتحسينها مؤخرًا. العمل عليها الآن سيسمح لنا برؤية كيفية استخدام AIObject بشكل عملي لإدارة المعرفة.
تجسيد AI_OOP: KnowledgeManager هو المكان الذي يتم فيه ربط AIObject (بمعادلاته و canonical_name) بالعالم اللغوي (عبر الربط اللغوي) وبالشبكة المعرفية (عبر الرسم البياني). العمل عليه سيجسد بشكل ملموس فلسفة AI_OOP المتكاملة.
أساس للوحدات المعرفية: KnowledgeManager هو المستودع المركزي للمعرفة الذي ستعتمد عليه جميع الوحدات المعرفية (cognitive_modules) لاحقًا (مثل LanguageModule, TheoryModule, ProblemSolverModule). بناء وتأكيد عمل هذا المستودع أولاً سيوفر أساسًا ثابتًا لهذه الوحدات.
التكامل مع الإثراء الخارجي: لقد قمنا بتعريف external_connectors/wikidata_connector.py واختباره. KnowledgeManager هو المكان الذي سيتم فيه استدعاء هذا الموصل لإثراء كائنات AIObject.
تأجيل التعقيدات المحددة: بينما calculus_engine.py مهم، إلا أن جزء التحويل العددي (_convert_equation_to_points) لا يزال معقدًا ويتطلب تطويرًا مستقبليًا. symbolic_logic_engine.py (Rete) يتطلب أيضًا تركيزًا كبيرًا. العمل على KnowledgeManager الآن يعتبر خطوة بناءة ومهمة دون الغوص في أعمق التعقيدات فورًا.
خطة العمل لـ foundations/knowledge_manager.py:
سنقوم بكتابة الكود الكامل لهذه الوحدة، مستفيدين من التصميم الذي ناقشناه واختبرناه سابقًا، مع التأكيد على:
استخدام AIObject كعقدة أساسية.
استخدام instance_id كمفتاح أساسي للكائنات و canonical_name للربط اللغوي.
استخدام networkx.MultiDiGraph للرسم البياني وتخزين ملخص بيانات AIObject في العقد و relation في الأضلاع.
دمج إدارة الربط اللغوي (الخرائط _linguistic_map و _reverse_linguistic_map).
التكامل السلس مع external_connectors في دالة add_object أو get_or_create_object.
توفير واجهات برمجة تطبيقات واضحة (add_object, get_object, add_relation, find_relations, query_graph, إلخ).
الاستعداد للتكامل مع StorageManager للحفظ والتحميل.
لنبدأ الآن بكتابة الكود الكامل لـ foundations/knowledge_manager.py.
'''

'''
تمام، لنبدأ الآن بكتابة الكود الكامل للوحدة foundations/knowledge_manager.py. هذه الوحدة، كما اتفقنا، ستكون مسؤولة عن إدارة قاعدة المعرفة بشكل مركزي، بما في ذلك تخزين كائنات AIObject الفعلية، إدارة الرسم البياني المعرفي (باستخدام NetworkX)، وإدارة الربط اللغوي.
'''

# OmniMind_v1.0/foundations/knowledge_manager.py

# -*- coding: utf-8 -*-
"""
===============================================================================
الوحدة: مدير المعرفة (Knowledge Manager) - OmniMind v1.0
===============================================================================

**الملف:** `knowledge_manager.py`

**الموقع:** `foundations/knowledge_manager.py`

**الوصف:**
يعمل هذا المكون كمدير مركزي ومتكامل للمعرفة في نظام OmniMind. يقوم بدمج:
1.  **إدارة الكائنات (`AIObject`):** التخزين المركزي والاسترجاع لكائنات AIObject
    الكاملة باستخدام معرفاتها الفريدة (`instance_id`).
2.  **إدارة الرسم البياني المعرفي:** استخدام `networkx.MultiDiGraph` لتمثيل
    العلاقات الهيكلية والمنطقية بين `AIObject`s. العقد في الرسم البياني
    تخزن ملخصًا لبيانات `AIObject` لتسهيل الاستعلام والتصور.
3.  **إدارة الربط اللغوي:** الحفاظ على الربط بين الأسماء الأساسية الحتمية
    (`canonical_name`) للكائنات وأسمائها في اللغات البشرية المختلفة.
4.  **إدارة الأفعال المنطقية (`Predicate`):** تعريف وتخزين الأفعال وخصائصها.
5.  **التكامل:** توفير واجهات للتكامل مع الموصلات الخارجية (`ExternalConnector`)
    ومحرك الاستدلال (`InferenceEngine`).

**الفئات المعرفة:**
-   `KnowledgeManager`: الفئة الرئيسية لإدارة قاعدة المعرفة والربط اللغوي.

**الاعتماديات:**
-   `networkx`: لإدارة الرسم البياني المعرفي. (ضرورية)
-   `typing`, `logging`, `collections.defaultdict`, `time`: أدوات بايثون الأساسية.
-   `..representations`: للوصول إلى `AIObject`, `ShapeEquation`, `ShapeComponent`.
-   `..external_connectors.base_connector` (تلميح نوع): للتعامل مع `ExternalConnector`.
-   `..inference.rete_engine` (تلميح نوع): للتعامل مع `InferenceEngine`.

**المساهمة في النظام:**
-   يوحد إدارة الكائنات، الرسم البياني، والربط اللغوي في مكان واحد.
-   يوفر واجهة API متسقة لإدارة المعرفة الأساسية.
-   يستخدم NetworkX MultiDiGraph للتمثيل المرن للعلاقات.
-   يحتفظ بالفهارس اللازمة للبحث السريع بالمعرف والاسم اللغوي والاسم الأساسي.
-   مصمم للتكامل السهل مع وحدات الإثراء والاستدلال.
"""

import logging
import time
from typing import Dict, Optional, Any, List, Tuple, Set, Union, Type
from collections import defaultdict
import itertools # لإعادة تعيين العدادات (إذا لم نستخدم عدادات الهياكل)

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    # تعريف وهمي لتجنب أخطاء لاحقة
    nx = type('nx', (object,), {'MultiDiGraph': lambda **kwargs: type('Graph', (object,), {'graph': {}, 'add_node': lambda *a, **k: None, 'add_edge': lambda *a, **k: None, 'has_node': lambda n: False, 'has_edge': lambda u, v, k=None: False, 'remove_node': lambda n: None, 'remove_edge': lambda u, v, k=None: None, 'nodes': type('NodesView', (object,), {'__call__': lambda s, data=False: {}, '__getitem__': lambda s, k: {}})(), 'edges': type('EdgesView', (object,), {'__call__': lambda s, data=False, keys=False: []})(), 'in_edges': lambda *a,**k: [], 'out_edges': lambda *a,**k: [], 'number_of_nodes': lambda: 0, 'number_of_edges': lambda: 0, 'clear': lambda: None})()})()
    print("خطأ فادح: مكتبة NetworkX غير مثبتة. KnowledgeManager لن يعمل بشكل كامل. قم بتثبيتها: pip install networkx")

# استيراد من داخل النظام
from ..representations import AIObject, ShapeEquation, ShapeComponent
# استيراد أنواع المكونات الأخرى (للتلميحات وتمرير المراجع)
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..external_connectors.base_connector import BaseConnector # افتراض وجود واجهة أساسية
    from ..inference.rete_engine import ReteNetwork # أو واجهة محرك الاستدلال

# تعريف أنواع أدق
ExternalConnector = Any # يمكن استبدالها بـ BaseConnector لاحقًا
InferenceEngine = Any   # يمكن استبدالها بـ ReteNetwork أو واجهة لاحقًا

logger = logging.getLogger(__name__)

# ============================================================== #
# ================ CLASS: KnowledgeManager ===================== #
# ============================================================== #
class KnowledgeManager:
    """
    يدير قاعدة المعرفة المكونة من كائنات AIObject، الرسم البياني لعلاقاتها،
    والربط اللغوي.
    """
    def __init__(self, external_connectors: Optional[List[ExternalConnector]] = None):
        """
        إنشاء مدير معرفة جديد.

        Args:
            external_connectors (Optional[List[ExternalConnector]]): قائمة بالموصلات الخارجية
                                                                    المراد استخدامها للإثراء.
        """
        if not NETWORKX_AVAILABLE:
            raise ImportError("NetworkX library is required for KnowledgeManager.")

        # --- مخزن الكائنات الرئيسي ---
        # يستخدم instance_id كمفتاح أساسي
        self._objects: Dict[str, AIObject] = {}

        # --- الرسم البياني المعرفي ---
        self.graph: nx.MultiDiGraph = nx.MultiDiGraph()
        self.graph.graph['name'] = "OmniMind Knowledge Graph v1.0"
        self.graph.graph['created_at'] = time.time()

        # --- الربط اللغوي والأسماء ---
        # canonical_name -> {lang_code: name}
        self._linguistic_map: Dict[str, Dict[str, str]] = defaultdict(dict)
        # lang_code -> {lower_case_name: canonical_name} (للبحث العكسي السريع)
        self._reverse_linguistic_map: Dict[str, Dict[str, str]] = defaultdict(dict)
        # فهرس إضافي: الاسم الأساسي -> قائمة بـ instance_ids التي تشترك فيه
        # مفيد للعثور على كل المثيلات التي لها نفس الشكل المنطقي
        self._canonical_name_to_ids: Dict[str, List[str]] = defaultdict(list)

        # --- تخزين الأفعال (بسيط حاليًا) ---
        self._predicates: Dict[str, Dict[str, Any]] = {} # name -> properties_dict

        # --- التكامل ---
        self.inference_engine: Optional[InferenceEngine] = None
        self.external_connectors: Dict[str, ExternalConnector] = {}
        if external_connectors:
            for connector in external_connectors:
                # استخدام اسم الفئة كمفتاح افتراضي أو خاصية معرفة
                name = getattr(connector, 'source_name', connector.__class__.__name__).lower()
                self.add_external_connector(name, connector)

        logger.info(f"Knowledge Manager initialized (NetworkX: {NETWORKX_AVAILABLE}).")

    # --- دوال إدارة الكائنات (Objects) ---

    def add_object(self, obj: AIObject, enrich: bool = True) -> AIObject:
        """
        إضافة/تحديث كائن AIObject في KM، مع الإثراء الاختياري إذا كان جديدًا.
        هذه هي الدالة المركزية والوحيدة لإدارة إدخال الكائنات.

        Args:
            obj (AIObject): الكائن المراد إضافته أو تحديثه.
            enrich (bool): هل يجب محاولة إثراء الكائن إذا كان جديدًا؟ الافتراضي True.

        Returns:
            AIObject: الكائن الذي تم إضافته أو تحديثه داخل KM.

        Raises:
            TypeError: إذا لم يكن المدخل من نوع AIObject.
            ValueError: إذا كان instance_id مستخدمًا لكائن مختلف منطقيًا (اسم أساسي مختلف).
        """
        if not isinstance(obj, AIObject):
            raise TypeError("Input must be an AIObject instance.")

        obj_id = obj.instance_id
        # التأكد من أن الاسم الأساسي محدث قبل أي عملية أخرى
        obj._update_canonical_name()
        obj_canon_name = obj.canonical_name

        is_new_instance = obj_id not in self._objects

        if not is_new_instance:
            # --- تحديث كائن موجود ---
            existing_obj = self._objects[obj_id]
            logger.debug(f"Updating existing AIObject {obj_id[:8]} ('{obj.name or obj_canon_name}')...")

            # التحقق من التناسق: هل يتطابق الاسم الأساسي؟
            if existing_obj.canonical_name != obj_canon_name:
                # هذا يعني أننا نحاول تحديث كائن بمعرف موجود ولكن بمعادلة مختلفة جذريًا!
                # هذا قد يشير إلى خطأ في مكان آخر (تكرار UUID؟) أو تغيير جوهري في فهم الكائن.
                # السياسة الحالية: السماح بالتحديث وتحديث الاسم الأساسي والفهارس المرتبطة.
                logger.warning(f"Canonical name mismatch for existing object {obj_id[:8]}! "
                               f"Old='{existing_obj.canonical_name}', New='{obj_canon_name}'. "
                               f"Updating equation and re-indexing.")
                # إزالة الفهرسة القديمة للاسم الأساسي
                if existing_obj.canonical_name in self._canonical_name_to_ids:
                     if obj_id in self._canonical_name_to_ids[existing_obj.canonical_name]:
                         self._canonical_name_to_ids[existing_obj.canonical_name].remove(obj_id)
                     if not self._canonical_name_to_ids[existing_obj.canonical_name]:
                         del self._canonical_name_to_ids[existing_obj.canonical_name]

            # دمج المعلومات من الكائن الجديد إلى الكائن الموجود
            # (يمكن جعل هذا المنطق أكثر تطورًا، مثلاً بالاعتماد على الطابع الزمني لكل خاصية)
            existing_obj.set_equation(obj.equation, obj.recognition_confidence) # التحديث سيغير canonical_name إذا لزم الأمر
            for lang, name in obj.linguistic_tags.items():
                 # دمج الوسوم اللغوية (add_linguistic_tag سيضيفها لـ aliases أيضًا)
                 existing_obj.add_linguistic_tag(lang, name)
            for key, value in obj.properties.items():
                 # تحديث الخصائص
                 existing_obj.update_property(key, value) # update_property تتجاهل التحديث إذا لم تتغير القيمة
            # دمج البيانات الوصفية (اختياري، قد نكتفي بالثقة والمصدر)
            existing_obj.metadata['confidence'] = max(existing_obj.metadata.get('confidence',0.0), obj.recognition_confidence)
            if obj.metadata.get('source', 'unknown') != 'unknown':
                 existing_obj.metadata['source'] = obj.metadata.get('source')
            existing_obj.metadata.setdefault('aliases', set()).update(obj.metadata.get('aliases', set()))
            existing_obj.metadata.setdefault('external_ids', {}).update(obj.metadata.get('external_ids', {}))
            existing_obj.metadata.setdefault('tags', set()).update(obj.metadata.get('tags', set()))
            existing_obj._update_timestamp() # التأكد من تحديث وقت التعديل

            # تحديث الفهارس والرسام البياني
            self._update_indices_for_object(existing_obj)
            self._update_graph_node(existing_obj)
            logger.debug(f"  Object {obj_id[:8]} updated.")
            return existing_obj

        else:
            # --- إضافة كائن جديد ---
            self._objects[obj_id] = obj
            self._update_indices_for_object(obj) # إضافة للفهارس
            self._update_graph_node(obj)         # إضافة للرسم البياني
            logger.info(f"+ Added new AIObject: {obj!r}")

            # محاولة الإثراء إذا كان مطلوبًا
            if enrich and self.external_connectors:
                if self._enrich_object_from_external(obj):
                    # إذا حدث إثراء، أعد تحديث الفهارس والرسم البياني
                    self._update_indices_for_object(obj)
                    self._update_graph_node(obj)
            return obj

    def _update_indices_for_object(self, obj: AIObject):
        """(داخلي) تحديث فهارس الربط اللغوي والاسم الأساسي لكائن."""
        obj_id = obj.instance_id
        canon_name = obj.canonical_name

        # 1. تحديث فهرس الاسم الأساسي -> قائمة المعرفات
        if canon_name:
             # التأكد من أن المعرف موجود في القائمة الصحيحة
             if obj_id not in self._canonical_name_to_ids[canon_name]:
                 self._canonical_name_to_ids[canon_name].append(obj_id)
                 self._canonical_name_to_ids[canon_name].sort() # للحفاظ على الترتيب

        # 2. تحديث خرائط الربط اللغوي (الأساسية والعكسية)
        # إزالة الارتباطات القديمة للاسم الأساسي (إذا تغير) - هذا معقد، الأسهل إعادة البناء عند التغيير
        # سنقوم ببساطة بتحديثها بناءً على linguistic_tags و aliases الحالية
        if canon_name:
            self._linguistic_map[canon_name] = obj.linguistic_tags.copy()
            # تحديث الخريطة العكسية
            for lang, name in obj.linguistic_tags.items():
                 self._reverse_linguistic_map[lang.lower()][name.lower()] = canon_name
            for alias in obj.metadata.get('aliases', set()):
                 if alias: # التأكد من أن الاسم المستعار ليس فارغًا
                      self._reverse_linguistic_map['alias'][alias.lower()] = canon_name

    def _update_graph_node(self, obj: AIObject):
        """(داخلي) إضافة أو تحديث عقدة في الرسم البياني تمثل AIObject."""
        if not NETWORKX_AVAILABLE: return
        node_id = obj.instance_id
        # تحضير ملخص البيانات للعقدة
        node_data = {
            'label': obj.get_linguistic_name('ar', default_to_english=True, default_to_canonical=True), # الاسم الأكثر قابلية للقراءة
            'canonical_name': obj.canonical_name,
            'type': 'AIObject', # يمكن تخصيصه أكثر لاحقًا
            'tags': list(obj.metadata.get('tags', [])), # تحويل لـ list للـ GML
            'properties_summary': {k: str(v)[:30] + ('...' if len(str(v))>30 else '')
                                   for k, v in list(obj.properties.items())[:5]}, # ملخص أول 5 خصائص
            'confidence': obj.recognition_confidence,
            'timestamp': obj.metadata.get('last_updated_at', 0.0),
            'source': obj.metadata.get('source', 'unknown')
        }
        # إضافة أو تحديث العقدة (NetworkX يدمج السمات تلقائيًا)
        self.graph.add_node(node_id, **{k:v for k,v in node_data.items() if v is not None}) # تجاهل قيم None
        # logger.debug(f"  Graph node {node_id[:8]} added/updated.")

    def get_object(self, identifier: str, lang: Optional[str] = None) -> Optional[AIObject]:
        """
        (مُحسّن) الحصول على كائن AIObject كامل بالمعرف الفريد (instance_id)،
        أو بالاسم الأساسي (canonical_name)، أو بالاسم اللغوي (linguistic tag).

        Args:
            identifier (str): المعرف أو الاسم المراد البحث عنه.
            lang (Optional[str]): رمز اللغة إذا كان المعرف اسمًا لغويًا.

        Returns:
            Optional[AIObject]: الكائن `AIObject` الكامل إذا تم العثور عليه، وإلا `None`.
        """
        if not isinstance(identifier, str): return None
        identifier_clean = identifier.strip()

        # 1. البحث بالـ instance_id (الأكثر دقة)
        if identifier_clean in self._objects:
            # logger.debug(f"get_object: Found by instance_id: {identifier_clean[:8]}")
            return self._objects[identifier_clean]

        # 2. البحث بالاسم الأساسي (canonical_name)
        ids_for_canon = self._canonical_name_to_ids.get(identifier_clean, [])
        if ids_for_canon:
            first_id = ids_for_canon[0]
            # logger.debug(f"get_object: Found by canonical_name '{identifier_clean}'. Returning first instance: {first_id[:8]}")
            return self._objects.get(first_id)

        # 3. البحث بالاسم اللغوي (linguistic tag)
        found_canon_name: Optional[str] = None
        # البحث في اللغة المحددة أولاً
        if lang:
            found_canon_name = self._reverse_linguistic_map.get(lang.lower(), {}).get(identifier_clean.lower())
        # إذا لم يوجد، ابحث في الأسماء البديلة (aliases)
        if not found_canon_name:
             found_canon_name = self._reverse_linguistic_map.get('alias', {}).get(identifier_clean.lower())
        # إذا لم يوجد، ابحث في جميع اللغات الأخرى (أقل كفاءة)
        if not found_canon_name:
             for lang_map in self._reverse_linguistic_map.values():
                 found_canon_name = lang_map.get(identifier_clean.lower())
                 if found_canon_name: break

        if found_canon_name:
            ids_for_lang = self._canonical_name_to_ids.get(found_canon_name, [])
            if ids_for_lang:
                 first_id = ids_for_lang[0]
                 logger.debug(f"get_object: Found by linguistic name '{identifier_clean}' (Canon='{found_canon_name}'). Returning instance: {first_id[:8]}")
                 return self._objects.get(first_id)

        logger.debug(f"get_object: Could not find AIObject for identifier '{identifier_clean}' (lang={lang}).")
        return None

    def get_or_create_object(self, name: str, lang: str = 'ar', enrich: bool = True, **kwargs) -> AIObject:
        # (نفس كود get_or_create_object السابق - يعتمد على get_object و add_object)
        existing_obj = self.get_object(name=name, lang=lang)
        if existing_obj:
            if 'confidence' in kwargs and kwargs['confidence'] > existing_obj.metadata.get('confidence',0.0):
                 existing_obj.metadata['confidence'] = max(0.0, min(1.0, kwargs['confidence']))
                 if 'source' in kwargs: existing_obj.metadata['source'] = kwargs['source']
                 existing_obj._update_timestamp()
            existing_obj.update_linguistic_features(
                gender=kwargs.get('gender') if kwargs.get('gender') != 'unknown' else None,
                number=kwargs.get('number') if kwargs.get('number') != 'unknown' else None
            )
            # إضافة الاسم كمستعار إذا لم يكن موجودًا بالفعل
            existing_obj.add_alias(name)
            return existing_obj
        else:
            # إنشاء كائن جديد (سيعطى ID تلقائيًا)
            # تمرير الاسم في linguistic_tags
            kwargs.setdefault('linguistic_tags', {})[lang] = name
            new_obj = AIObject(name=name, **kwargs) # تمرير الاسم للمنشئ لتسهيل الأمور
            return self.add_object(new_obj, enrich=enrich) # add_object سيتعامل مع الإثراء والفهرسة


    # --- دوال إدارة الأفعال (Predicates) ---
    # (لا تغيير جوهري عن النسخة السابقة - بسيطة وتعتمد على قاموس)
    def get_predicate(self, name: str) -> Optional[Dict[str, Any]]:
        """الحصول على خصائص الفعل المنطقي باسمه."""
        return self._predicates.get(name.strip())

    def define_predicate_properties(self, name: str, symmetric: bool = False,
                                    inverse_name: Optional[str] = None, transitive: bool = False):
        """تعريف أو تحديث خصائص فعل منطقي."""
        clean_name = name.strip()
        if not clean_name: raise ValueError("Predicate name cannot be empty.")
        clean_inverse = inverse_name.strip() if inverse_name else None

        props = {
            'name': clean_name, # تخزين الاسم مع الخصائص
            'symmetric': symmetric,
            'inverse_name': clean_inverse,
            'transitive': transitive
        }
        if clean_name not in self._predicates or self._predicates[clean_name] != props:
             logger.info(f"Defining/Updating predicate '{clean_name}': {props}")
             self._predicates[clean_name] = props
             # ضمان التناسق للعكس
             if clean_inverse:
                  inv_props = self._predicates.get(clean_inverse, {'name': clean_inverse}) # الحصول على خصائص العكس أو إنشاء قاموس جديد
                  # تحديث عكس العكس فقط إذا كان مختلفًا
                  if inv_props.get('inverse_name') != clean_name:
                       logger.info(f"  Ensuring inverse consistency: Setting inverse of '{clean_inverse}' to '{clean_name}'.")
                       inv_props['inverse_name'] = clean_name
                       # يمكن نسخ الخصائص الأخرى (مثل التماثل) هنا إذا لزم الأمر
                       self._predicates[clean_inverse] = inv_props # تحديث أو إضافة العكس


    # --- دوال إدارة العلاقات (Relations) ---
    # (تعتمد على AIObject و Predicate name)

    def add_relation(self, subject: AIObject, predicate_name: str, obj: AIObject,
                     check_duplicates: bool = True, check_conflict: bool = True,
                     **metadata) -> Optional[str]: # تُرجع instance_id للرابط المضاف أو الموجود
        """
        إضافة علاقة جديدة (ثلاثية S-P-O) إلى الرسم البياني المعرفي.
        تستخدم معرفات الكائنات كعقد وأسماء الأفعال كتسميات للأضلاع.

        Args:
            subject (AIObject): الكائن الفاعل.
            predicate_name (str): اسم الفعل المنطقي.
            obj (AIObject): الكائن المفعول.
            check_duplicates (bool): هل يجب التحقق من وجود علاقة مطابقة تمامًا قبل الإضافة؟
            check_conflict (bool): هل يجب التحقق من التناقضات المحتملة؟
            **metadata: بيانات وصفية إضافية للعلاقة (مثل source, confidence, timestamp).

        Returns:
            Optional[str]: معرف instance_id للضلع المضاف (NetworkX قد لا يوفر ID ثابت)،
                           أو None إذا لم تتم الإضافة.
                           (ملاحظة: سنستخدم مفتاحًا مركبًا للضلع بدلاً من ID.)

        Raises:
            ValueError: إذا كان الفاعل أو المفعول غير مضافين لـ KM، أو اسم الفعل فارغ.
        """
        if not isinstance(subject, AIObject) or subject.instance_id not in self._objects:
            raise ValueError(f"Subject object (ID: {getattr(subject,'instance_id','N/A')}) not managed by this KnowledgeManager.")
        if not isinstance(obj, AIObject) or obj.instance_id not in self._objects:
            raise ValueError(f"Object object (ID: {getattr(obj,'instance_id','N/A')}) not managed by this KnowledgeManager.")
        clean_predicate_name = predicate_name.strip()
        if not clean_predicate_name:
            raise ValueError("Predicate name cannot be empty.")

        # التأكد من تعريف الفعل المنطقي (يمكن إنشاؤه بخصائص افتراضية)
        if clean_predicate_name not in self._predicates:
             logger.warning(f"Predicate '{clean_predicate_name}' not explicitly defined. Adding with default properties.")
             self.define_predicate_properties(clean_predicate_name)

        # --- التحقق من التكرار باستخدام الرسم البياني ---
        # مفتاح الضلع يمكن أن يكون مجرد اسم الفعل إذا لم نتوقع علاقات متعددة بنفس النوع
        # أو يمكن استخدام مفتاح أكثر تعقيدًا (مثل تجزئة البيانات الوصفية؟)
        # حاليًا، نستخدم اسم الفعل كمفتاح ونسمح بأضلاع متعددة (MultiDiGraph)
        edge_key = clean_predicate_name # استخدام اسم الفعل كمفتاح بسيط للضلع

        if check_duplicates and self.graph.has_edge(subject.instance_id, obj.instance_id, key=edge_key):
            # علاقة بنفس الفاعل والفعل والمفعول موجودة بالفعل
            existing_edge_data = self.graph.get_edge_data(subject.instance_id, obj.instance_id, key=edge_key)
            logger.debug(f"Relation {subject.canonical_name}-{clean_predicate_name}-{obj.canonical_name} already exists in graph. Updating metadata.")
            # تحديث البيانات الوصفية للضلع الموجود (مثال: الثقة الأعلى)
            # (NetworkX v3+ required for update)
            new_confidence = metadata.get('confidence', 1.0)
            if new_confidence > existing_edge_data.get('confidence', 0.0):
                 attrs_to_update = {'confidence': new_confidence}
                 if 'source' in metadata: attrs_to_update['source'] = metadata['source']
                 if 'timestamp' in metadata: attrs_to_update['timestamp'] = metadata['timestamp']
                 nx.set_edge_attributes(self.graph, {(subject.instance_id, obj.instance_id, edge_key): attrs_to_update})
            return edge_key # إرجاع مفتاح الضلع الموجود

        # --- التحقق من التناقضات (منطق مبسط) ---
        # (يمكن تحسين هذا ليشمل ConflictResolver)
        if check_conflict:
            pred_props = self._predicates.get(clean_predicate_name, {})
            inverse_pred_name = pred_props.get('inverse_name')
            # تحقق إذا كانت العلاقة العكسية موجودة بشكل يتعارض
            # مثال بسيط: A يملك B ومحاولة إضافة B يملك A
            if inverse_pred_name and inverse_pred_name == clean_predicate_name: # حالة العكس هو نفسه (نادراً)
                 pass # لا تعارض مباشر
            elif inverse_pred_name:
                 inverse_key = inverse_pred_name
                 if self.graph.has_edge(obj.instance_id, subject.instance_id, key=inverse_key):
                      logger.warning(f"Potential conflict detected for {subject.canonical_name}-{clean_predicate_name}-{obj.canonical_name}. "
                                     f"Inverse relation exists: {obj.canonical_name}-{inverse_pred_name}-{subject.canonical_name}. Adding anyway.")
                      # لا نمنع الإضافة حاليًا

        # --- إضافة الضلع الجديد ---
        edge_attributes = {
            'label': clean_predicate_name, # اسم الفعل كتسمية
            'timestamp': time.time(),
            # إضافة البيانات الوصفية الممررة
            **metadata
        }
        # التأكد من أن القيم قابلة للتخزين في NetworkX (نصوص، أرقام، قيم منطقية)
        sanitized_attributes = {k: (str(v) if isinstance(v, (list, dict, set)) else v)
                                for k, v in edge_attributes.items() if v is not None}

        self.graph.add_edge(subject.instance_id, obj.instance_id, key=edge_key, **sanitized_attributes)
        logger.info(f"+ Relation Added to Graph: {subject.canonical_name} -[{clean_predicate_name}]-> {obj.canonical_name} (Key: {edge_key})")

        # --- إخطار محرك الاستدلال (Rete) ---
        if self.inference_engine and hasattr(self.inference_engine, 'add_fact'):
            # بناء كائن Relation مؤقت لتمريره للمحرك
            temp_relation = Relation(subject=subject, predicate=Predicate(clean_predicate_name), obj=obj,
                                     metadata=metadata) # يجب أن تحصل Predicate على خصائصها من KB
            predicate_obj = self.get_predicate_object(clean_predicate_name) # دالة مساعدة جديدة
            if predicate_obj: temp_relation.predicate = predicate_obj
            try:
                self.inference_engine.add_fact(temp_relation)
            except Exception as e_inf:
                logger.error(f"!!! Error passing fact to inference engine: {e_inf}", exc_info=True)

        return edge_key

    def remove_relation(self, subject: AIObject, predicate_name: str, obj: AIObject, key: Optional[str] = None) -> bool:
        """
        إزالة علاقة (ضلع) من الرسم البياني.

        Args:
            subject (AIObject): الكائن الفاعل.
            predicate_name (str): اسم الفعل المنطقي.
            obj (AIObject): الكائن المفعول.
            key (Optional[str]): مفتاح الضلع المحدد (إذا كان هناك أضلاع متعددة بنفس النوع).
                                 إذا كان None، يتم استخدام اسم الفعل كمفتاح افتراضي.

        Returns:
            bool: True إذا تم العثور على الضلع وإزالته بنجاح.
        """
        if not NETWORKX_AVAILABLE: return False
        edge_key = key if key is not None else predicate_name.strip()
        subj_id = subject.instance_id
        obj_id = obj.instance_id

        if self.graph.has_edge(subj_id, obj_id, key=edge_key):
            try:
                self.graph.remove_edge(subj_id, obj_id, key=edge_key)
                logger.info(f"- Relation Removed from Graph: {subj_id[:8]} -[{edge_key}]-> {obj_id[:8]}")
                # TODO: إخطار Rete بالحذف (يتطلب remove_fact)
                # if self.inference_engine and hasattr(self.inference_engine, 'remove_fact'):
                #     temp_relation = Relation(...)
                #     self.inference_engine.remove_fact(temp_relation)
                return True
            except Exception as e:
                 logger.error(f"Error removing edge {subj_id[:8]}-{edge_key}->{obj_id[:8]}: {e}", exc_info=True)
                 return False
        else:
            # logger.debug(f"Edge {subj_id[:8]}-{edge_key}->{obj_id[:8]} not found for removal.")
            return False

    def find_relations(self, subject: Optional[AIObject] = None,
                       predicate_name: Optional[str] = None,
                       obj: Optional[AIObject] = None) -> List[Dict[str, Any]]:
        """
        البحث عن علاقات (أضلاع) مطابقة للمعايير في الرسم البياني.
        ترجع قائمة بقواميس تمثل الأضلاع المطابقة مع بياناتها.

        Args:
            subject (Optional[AIObject]): الكائن الفاعل.
            predicate_name (Optional[str]): اسم الفعل (تسمية الضلع/المفتاح).
            obj (Optional[AIObject]): الكائن المفعول.

        Returns:
            List[Dict[str, Any]]: قائمة بقواميس، كل قاموس يصف ضلعًا مطابقًا
                                  ويتضمن 'source', 'target', 'key', وجميع سماته.
        """
        if not NETWORKX_AVAILABLE: return []
        results = []
        subj_id = subject.instance_id if subject else None
        obj_id = obj.instance_id if obj else None
        pred_key = predicate_name.strip() if predicate_name else None

        # اختيار الطريقة الأمثل للبحث في NetworkX
        edges_iterator: Any = None
        if subj_id and obj_id: # البحث بين عقدتين محددتين
             if self.graph.has_node(subj_id) and self.graph.has_node(obj_id):
                  # الحصول على كل الأضلاع بينهما
                  edges_data = self.graph.get_edge_data(subj_id, obj_id, default={})
                  # الترشيح حسب المفتاح (اسم الفعل) إذا تم تحديده
                  edges_iterator = [(subj_id, obj_id, k, d) for k, d in edges_data.items() if pred_key is None or k == pred_key]
             else: edges_iterator = []
        elif subj_id: # البحث عن الأضلاع الصادرة من فاعل معين
             edges_iterator = self.graph.out_edges(subj_id, keys=True, data=True)
        elif obj_id: # البحث عن الأضلاع الواردة لمفعول معين
             edges_iterator = self.graph.in_edges(obj_id, keys=True, data=True)
        else: # البحث عن جميع الأضلاع (قد يكون مكلفًا)
             edges_iterator = self.graph.edges(keys=True, data=True)

        # تصفية النتائج حسب المعايير المتبقية وتنسيقها
        for u, v, k, data in edges_iterator:
            # إذا كنا نبحث عن فعل معين ولم يتم ترشيحه أعلاه
            if pred_key is not None and k != pred_key:
                 continue
            # إذا كنا نبحث عن مفعول معين (وكان البحث بالفاعل أو الكل)
            if obj_id is not None and v != obj_id:
                 continue
            # إذا كنا نبحث عن فاعل معين (وكان البحث بالمفعول أو الكل)
            if subj_id is not None and u != subj_id:
                 continue

            # تنسيق النتيجة
            results.append({
                'source_id': u,
                'target_id': v,
                'key': k, # مفتاح الضلع (عادة اسم الفعل)
                **data # إضافة جميع سمات الضلع
            })

        # logger.debug(f"find_relations found {len(results)} matching edges.")
        return results

    def query_relations_for_graph(self, subject_name: Optional[str] = None,
                                  predicate_name: Optional[str] = None,
                                  object_name: Optional[str] = None) -> Dict[str, List[Dict]]:
        """
        إجراء استعلام وإرجاع النتائج بصيغة مناسبة لتصور الرسم البياني (nodes/links).
        (تستخدم find_relations داخليًا).
        """
        subj = self.get_object(name=subject_name) if subject_name else None
        obj = self.get_object(name=object_name) if object_name else None
        found_relations_data = self.find_relations(subject=subj, predicate_name=predicate_name, obj=obj)

        nodes_dict: Dict[str, Dict] = {} # instance_id -> node_data
        links: List[Dict] = []

        for edge_data in found_relations_data:
            source_id = edge_data['source_id']
            target_id = edge_data['target_id']
            edge_key = edge_data['key'] # اسم الفعل عادة

            # إضافة العقد إذا لم تكن موجودة
            for node_id in [source_id, target_id]:
                if node_id not in nodes_dict:
                     node_graph_data = self.graph.nodes.get(node_id, {}) # الحصول على بيانات العقدة من الرسم
                     if node_graph_data: # التأكد من وجود العقدة في الرسم
                         nodes_dict[node_id] = {
                             'id': node_id, # مهم لتحديد العقدة
                             'name': node_graph_data.get('label', node_id[:8]), # استخدام label من الرسم
                             # إضافة سمات أخرى من الرسم البياني إذا رغبت
                             'type': node_graph_data.get('type', 'Unknown'),
                             'canonical_name': node_graph_data.get('canonical_name'),
                         }

            # إضافة الرابط
            link_data = {
                'source': source_id, # استخدام ID للربط
                'target': target_id,
                'type': edge_key, # اسم الفعل
                # إضافة بيانات وصفية أخرى للرابط من edge_data
                'relation_label': edge_data.get('label', edge_key),
                'confidence': edge_data.get('confidence'),
                'source_text': edge_data.get('source'),
                'timestamp': edge_data.get('timestamp')
            }
            links.append({k:v for k,v in link_data.items() if v is not None}) # إزالة قيم None

        return {'nodes': list(nodes_dict.values()), 'links': links}

    # --- دوال التكامل ---
    def set_inference_engine(self, engine: InferenceEngine):
        # (نفس السابق)
        self.inference_engine = engine
        if hasattr(engine, 'kb_ref'): engine.kb_ref = self # Rete يحتاج لمرجع KB
        logger.info(f"Inference engine ({type(engine).__name__}) linked to KnowledgeManager.")

    def run_inference(self, use_simple_loop_if_no_engine=False, **kwargs) -> int:
        """تشغيل الاستدلال (المحرك المرتبط أو الحلقة البسيطة كاحتياطي)."""
        if self.inference_engine and hasattr(self.inference_engine, 'run'):
            try: return self.inference_engine.run(**kwargs) or 0
            except Exception as e_inf: logger.error(f"Error running inference engine: {e_inf}"); return 0
        elif use_simple_loop_if_no_engine and hasattr(self, '_inference_rules'):
             from ..inference.simple_loop import run_simple_inference_loop # استيراد مؤقت
             return run_simple_inference_loop(self, getattr(self, '_inference_rules', []), **kwargs)
        else: logger.warning("No inference engine linked or rules for simple loop."); return 0

    def add_external_connector(self, source_db_name: str, connector: ExternalConnector):
        # (نفس السابق)
        self.external_connectors[source_db_name.lower()] = connector
        logger.info(f"External connector added: '{source_db_name.lower()}'.")

    # --- دوال المساعدة والعرض ---
    @property
    def objects(self) -> List[AIObject]: return list(self._objects.values())
    # لا يوجد وصول مباشر لـ Predicate objects، فقط خصائصها
    # @property
    # def predicates(self) -> List[Predicate]: return list(self._predicates.values()) # لا يوجد Predicate objects
    def get_predicate_object(self, name: str) -> Optional[Predicate]:
         """(مساعد) إنشاء كائن Predicate مؤقت من الخصائص المخزنة."""
         props = self._predicates.get(name.strip())
         if props: return Predicate(**props) # استخدام ** لتمرير القاموس كـ kwargs
         return None
    @property
    def relations_graph_summary(self) -> str: # تعديل الاسم
        """إرجاع ملخص لعدد العقد والأضلاع في الرسم البياني."""
        if NETWORKX_AVAILABLE:
             return f"Graph: {self.graph.number_of_nodes()} Nodes, {self.graph.number_of_edges()} Edges"
        else: return "Graph: NetworkX not available."
    def __len__(self) -> int: return len(self._objects) # الطول هو عدد الكائنات
    def __repr__(self) -> str:
        return f"<KnowledgeManager v1.0 | AIObjects: {len(self._objects)}, Predicates: {len(self._predicates)}, {self.relations_graph_summary}>"
    def print_summary(self, max_items: int = 10):
        # (نفس السابق، مع تعديل لعرض AIObjects)
        print(f"\n=== KnowledgeManager Summary (v1.0) ===")
        print(f"  - AIObjects ({len(self._objects)}):")
        for i, obj in enumerate(self._objects.values()):
            if i >= max_items: print(f"    ... ({len(self._objects) - i} more)"); break
            print(f"    - {obj!r}") # استخدام repr لـ AIObject
        print(f"\n  - Predicates ({len(self._predicates)}):")
        for i, (name, props) in enumerate(self._predicates.items()):
            if i >= max_items: print(f"    ... ({len(self._predicates) - i} more)"); break
            print(f"    - Name='{name}', Props={props}")
        print(f"\n  - Relations ({self.graph.number_of_edges()} in graph):") # عرض عدد الأضلاع
        # عرض أول N أضلاع كأمثلة
        edge_count = 0
        for u, v, k, data in self.graph.edges(keys=True, data=True):
            if edge_count >= max_items: print(f"    ... ({self.graph.number_of_edges() - edge_count} more)"); break
            # محاولة الحصول على أسماء الكائنات للعرض
            subj_name = self._objects.get(u, AIObject(name=f"ID_{u[:4]}")).get_linguistic_name('ar', default_to_canonical=True)
            obj_name = self._objects.get(v, AIObject(name=f"ID_{v[:4]}")).get_linguistic_name('ar', default_to_canonical=True)
            print(f"    - {subj_name} -[{k}]-> {obj_name} (Conf: {data.get('confidence', 'N/A'):.2f}, Src: {data.get('source', '?')})")
            edge_count += 1
        print(f"\n  {self.relations_graph_summary}")
        print(f"========================================")

# --- نهاية ملف knowledge_manager.py ---

'''
شرح التحسينات الرئيسية في KnowledgeManager (v1.0):
الاعتماد الكلي على AIObject:
_objects: هو القاموس الرئيسي الذي يخزن كائنات AIObject الكاملة (بما فيها معادلاتها وجميع بياناتها الوصفية) باستخدام instance_id كمفتاح.
الدوال مثل add_object, get_object, get_or_create_object تتعامل الآن مباشرة مع AIObject.
فصل الرسم البياني عن مخزن العلاقات:
self.graph (من نوع nx.MultiDiGraph): يُستخدم لتمثيل هيكل العلاقات بين الكائنات (AIObject.instance_id). العقد في الرسم تخزن فقط ملخصًا لبيانات AIObject (التسمية، النوع، إلخ) لتسهيل الاستعلام السريع والتصور. الأضلاع تمثل العلاقات وتخزن اسمها (كمفتاح أو تسمية) وبياناتها الوصفية (مصدر، ثقة، زمن).
self._relations (من الإصدارات السابقة) تمت إزالته. لم نعد بحاجة لتخزين كائنات Relation بشكل منفصل، حيث أن المعلومات الجوهرية للعلاقة (الفاعل، الفعل، المفعول، البيانات الوصفية) مخزنة الآن كضلع في الرسم البياني self.graph.
إدارة الأفعال (Predicate):
تم تبسيطها لتخزين خصائص الفعل (symmetric, inverse_name, transitive) في قاموس _predicates باستخدام اسم الفعل كمفتاح. لم نعد بحاجة لفئة Predicate كهيكل بيانات مستقل داخل KnowledgeManager إلا إذا أردنا إضافة خصائص أكثر تعقيدًا للأفعال لاحقًا. تم إنشاء دالة مساعدة get_predicate_object لإعادة بناء كائن Predicate مؤقت عند الحاجة (مثل تمريره لمحرك الاستدلال).
إدارة العلاقات (add_relation, remove_relation, find_relations):
تتعامل الآن مباشرة مع الرسم البياني (self.graph).
add_relation: تضيف ضلعًا إلى self.graph بين معرفي الفاعل والمفعول. اسم الفعل يُستخدم كمفتاح (key) للضلع (مفيد للسماح بعلاقات متعددة بنفس النوع إذا كان MultiDiGraph) وكـ label للوضوح. البيانات الوصفية للعلاقة تُخزن كسمات للضلع. يتم إخطار محرك الاستدلال بتمرير كائن Relation مؤقت يتم إنشاؤه لهذا الغرض.
remove_relation: تحذف الضلع المقابل من الرسم البياني.
find_relations: تبحث عن أضلاع مطابقة للمعايير في الرسم البياني وتُرجع قائمة بقواميس تمثل بيانات هذه الأضلاع (بما في ذلك معرفات المصدر والهدف، المفتاح/التسمية، والسمات).
الربط اللغوي (_linguistic_map, _reverse_linguistic_map):
تربط الآن canonical_name (المشتق من AIObject.equation) بالأسماء اللغوية في linguistic_tags.
تُستخدم في get_object للبحث بالاسم.
الإثراء الخارجي (_enrich_object_from_external):
تم تحسينها لتحديث كائن AIObject مباشرة بالمعلومات المسترجعة.
تستدعي add_relation لإضافة علاقات isA المستنتجة من Wikidata.
تضمن تحديث الفهارس والرسم البياني بعد الإثراء.
العرض (print_summary): تم تعديلها لتعرض ملخصًا لكائنات AIObject المخزنة، خصائص الأفعال، وعينة من الأضلاع (العلاقات) الموجودة في الرسم البياني.
الخلاصة:
هذه النسخة من KnowledgeManager أصبحت الآن متكاملة بشكل وثيق مع مفهوم AIObject والرسم البياني المعرفي. هي توفر أساسًا قويًا لإدارة المعرفة الهجينة (الرمزية والهيكلية) وتدعم التكامل مع الوحدات الأخرى بشكل فعال.
الخطوة التالية:
الآن بعد أن أصبح لدينا KnowledgeManager القادر على إدارة AIObject وعلاقاتها، يمكننا الانتقال إلى:
foundations/calculus_engine.py: مراجعة سريعة لضمان تكامله مع EquationManager و AIObject (خاصة دالة _convert_equation_to_points).
foundations/pattern_engine.py: مراجعة سريعة للتأكد من أنه يستخدم AIObject (أو سماته) في learn_pattern و recognize_pattern.
foundations/symbolic_logic_engine.py (Rete): التأكد من أنه يتفاعل بشكل صحيح مع KnowledgeManager الجديد (خاصة add_fact و TerminalNode.action التي قد تحتاج الآن لاستدعاء kb.add_relation).
cognitive_modules/: البدء في تنفيذ الوحدات المعرفية التي تعتمد بشكل كبير على KnowledgeManager (مثل LanguageModule, TheoryModule, ProblemSolverModule).
أقترح مراجعة سريعة لـ calculus_engine.py و pattern_engine.py (الخيار 1 و 2) للتأكد من توافقهما، ثم الانتقال إلى مراجعة وتكييف symbolic_logic_engine.py (الخيار 3) ليعمل مع KnowledgeManager الجديد. ما رأيك؟

'''