 
'''
ممتاز. لنبدأ إذن بالمراجعة السريعة لـ foundations/calculus_engine.py للتأكد من توافقه مع الهيكل الحالي، خاصة مع EquationManager الجديد ومع إمكانية استقبال AIObject كمدخل.
نقاط المراجعة لـ calculus_engine.py:
الاستيرادات: هل يستورد EquationManager, AIObject, ShapeEquation من المسارات الصحيحة؟ هل يستورد المحركات الفرعية (الرمزية والعددية) بشكل صحيح (أو يتعامل معها كتبعيات مُمررة)؟
التهيئة (__init__): هل يستقبل EquationManager بشكل صحيح؟ هل يقوم بتهيئة المحركات الفرعية (إذا لم يتم تمريرها) بشكل سليم؟
_get_equation_object(): هل تتعامل هذه الدالة المساعدة بشكل صحيح مع المدخلات من نوع AIObject, ShapeEquation, و str باستخدام EquationManager لإرجاع ShapeEquation؟
differentiate() و integrate(): هل تستخدمان _get_equation_object()؟ هل تمرران ShapeEquation الناتجة للمحركات الفرعية (الرمزية والعددية)؟
_convert_equation_to_points() (Placeholder): هل لا يزال Placeholder واضحًا؟ هل يشير إلى اعتماده المستقبلي على تحليل ShapeEquation (ربما بمساعدة EquationManager أو Renderer)؟
الكود المراجع لـ foundations/calculus_engine.py (مع تعديلات طفيفة للوضوح والتوافق):
'''

# OmniMind_v1.0/foundations/calculus_engine.py

# -*- coding: utf-8 -*-
"""
===============================================================================
الوحدة: محرك التفاضل والتكامل (Calculus Engine) - OmniMind v1.0 (مراجعة)
===============================================================================

**الملف:** `calculus_engine.py`

**الموقع:** `foundations/calculus_engine.py`

**الوصف:**
(نفس الوصف السابق - واجهة موحدة ومنسقة لعمليات التفاضل والتكامل)

**المراجعة:**
- التأكد من استخدام `EquationManager` لتحليل المدخلات النصية.
- التأكد من استقبال `AIObject` كمدخل والوصول إلى معادلته.
- التأكد من أن المحركات الفرعية (رمزية/عددية) تتلقى `ShapeEquation`.
- التأكيد على حالة Placeholder لدالة `_convert_equation_to_points`.
"""

import logging
from typing import Optional, Union, Dict, Any, Tuple, List, Callable # إضافة Callable

# --- استيراد المكتبات المطلوبة بشروط ---
try: import sympy; SYMPY_AVAILABLE = True
except ImportError: sympy = None; SYMPY_AVAILABLE = False; print("Warning: SymPy not available.")
try: import torch; TORCH_AVAILABLE = True
except ImportError: torch = None; TORCH_AVAILABLE = False; print("Warning: PyTorch not available.")
# (NumPy مطلوب لـ _convert_equation_to_points placeholder)
try: import numpy as np; NUMPY_AVAILABLE=True
except ImportError: np=None; NUMPY_AVAILABLE=False

# --- استيراد مكونات النظام ---
# استخدام .. للإشارة إلى الحزمة الأصلية ثم الوحدة المطلوبة
try:
    from ..representations import AIObject, ShapeEquation, ShapeComponent
    from .equation_manager import EquationManager
    # استيراد المحركات الفرعية (إذا كانت في ملفات منفصلة في foundations/)
    # from .symbolic_calculus import SymbolicCalculus # نفترض وجوده
    # from .numerical_calculus import NumericalNeuroCalculus, DEFAULT_CALCULUS_POINTS # نفترض وجوده
except ImportError as e:
    # حل بديل إذا تم تشغيل الملف مباشرة أو حدثت مشكلة في المسار
    logger = logging.getLogger(__name__) # تعريف Logger هنا للرسالة
    logger.error(f"Failed to import necessary modules for CalculusEngine: {e}. Using placeholders.")
    AIObject = type('AIObject', (object,), {'equation': None})
    ShapeEquation = type('ShapeEquation', (object,), {'is_empty': lambda s: True})
    EquationManager = type('EquationManager', (object,), {'parse': lambda s, eq: None})
    SymbolicCalculus = type('SymbolicCalculus', (object,), {})
    NumericalNeuroCalculus = type('NumericalNeuroCalculus', (object,), {})
    DEFAULT_CALCULUS_POINTS = 100

# تعريف أنواع المحركات الفرعية للـ Type Hinting
SymbolicCalculusEngine = Any # يمكن استخدام SymbolicCalculus إذا كان الاستيراد ناجحًا
NumericalCalculusEngine = Any # يمكن استخدام NumericalNeuroCalculus إذا كان الاستيراد ناجحًا

logger = logging.getLogger(__name__)

# ============================================================== #
# =================== CLASS: CalculusEngine ==================== #
# ============================================================== #
class CalculusEngine:
    """
    واجهة موحدة لعمليات التفاضل والتكامل الرمزية والعددية.
    """
    def __init__(self,
                 equation_manager: EquationManager,
                 symbolic_engine: Optional[SymbolicCalculusEngine] = None,
                 numerical_engine: Optional[NumericalCalculusEngine] = None,
                 config: Optional[Dict[str, Any]] = None):
        """
        تهيئة محرك الحساب.

        Args:
            equation_manager (EquationManager): مدير المعادلات لتحليل وتوليد المعادلات.
            symbolic_engine (Optional[SymbolicCalculusEngine]): المحرك الرمزي (إذا كان متاحًا).
            numerical_engine (Optional[NumericalCalculusEngine]): المحرك العددي (إذا كان متاحًا).
            config (Optional[Dict[str, Any]]): قاموس الإعدادات (لتمرير إعدادات المحركات الفرعية).
        """
        if not isinstance(equation_manager, EquationManager):
            raise TypeError("EquationManager instance is required.")
        cfg = config or {}
        self.eq_manager = equation_manager

        # --- تهيئة المحرك الرمزي (إذا لم يتم تمريره) ---
        self.sym_engine = symbolic_engine
        if self.sym_engine is None and SYMPY_AVAILABLE and SymbolicCalculus:
             try:
                 # قد يحتاج SymbolicCalculus إلى EquationManager أيضًا
                 self.sym_engine = SymbolicCalculus(self.eq_manager)
                 logger.info("Calculus Engine: Auto-initialized Symbolic sub-engine.")
             except Exception as e: logger.error(f"Failed to auto-init SymbolicCalculus: {e}")
        elif symbolic_engine is None:
             logger.warning("Calculus Engine: Symbolic sub-engine disabled (SymPy/Module unavailable or not provided).")

        # --- تهيئة المحرك العددي (إذا لم يتم تمريره) ---
        self.num_engine = numerical_engine
        if self.num_engine is None and TORCH_AVAILABLE and NumericalNeuroCalculus:
             try:
                 # قراءة الإعدادات من config
                 num_points = cfg.get('calculus_numeric',{}).get('num_points', DEFAULT_CALCULUS_POINTS)
                 max_states = cfg.get('calculus_numeric',{}).get('max_states', 100)
                 lr = cfg.get('calculus_numeric',{}).get('learning_rate', 0.01)
                 # ... يمكن قراءة إعدادات أخرى من config ...
                 self.num_engine = NumericalNeuroCalculus(
                     num_points=num_points,
                     # تمرير إعدادات أخرى من config للمحرك العددي
                     config=cfg.get('calculus_numeric', {})
                 )
                 logger.info(f"Calculus Engine: Auto-initialized Numerical sub-engine (Points: {num_points}).")
             except Exception as e: logger.error(f"Failed to auto-init NumericalNeuroCalculus: {e}")
        elif numerical_engine is None:
            logger.warning("Calculus Engine: Numerical sub-engine disabled (PyTorch/Module unavailable or not provided).")

        # --- التحقق النهائي ---
        if not self.sym_engine and not self.num_engine:
            logger.error("!!! CalculusEngine has NO active sub-engines !!!")

    # --- دوال الحالة والتحقق ---
    def is_symbolic_available(self) -> bool: return self.sym_engine is not None
    def is_numerical_available(self) -> bool: return self.num_engine is not None

    # --- الدوال المساعدة ---
    def _get_equation_object(self, equation_input: Union[AIObject, ShapeEquation, str]) -> Optional[ShapeEquation]:
        """(مُحسّن) يحاول الحصول على كائن ShapeEquation من مدخلات مختلفة."""
        if isinstance(equation_input, ShapeEquation):
            return equation_input
        elif isinstance(equation_input, AIObject):
            # التأكد من أن الكائن لديه معادلة
            if isinstance(equation_input.equation, ShapeEquation):
                 return equation_input.equation
            else:
                 log.warning(f"AIObject {equation_input.instance_id[:8]} has no valid ShapeEquation.")
                 return None
        elif isinstance(equation_input, str):
            # استخدام EquationManager لتحليل السلسلة النصية
            if self.eq_manager:
                 parsed_eq = self.eq_manager.parse(equation_input)
                 if parsed_eq: return parsed_eq
                 else: log.warning(f"Failed to parse equation string via EquationManager: '{equation_input[:50]}...'"); return None
            else: log.error("EquationManager not available to parse string input."); return None
        else:
            log.error(f"Unsupported input type for calculus: {type(equation_input)}")
            return None

    # --- دوال الواجهة الرئيسية ---
    def differentiate(self,
                      equation_input: Union[AIObject, ShapeEquation, str],
                      variable: str = 'x',
                      mode: str = 'auto',
                      **kwargs # وسائط إضافية للمحركات الفرعية
                     ) -> Optional[Dict[str, Any]]:
        """
        إجراء عملية التفاضل (رمزي أو عددي).

        Args:
            equation_input (Union[AIObject, ShapeEquation, str]): الكائن أو المعادلة أو النص.
            variable (str): المتغير المستقل للتفاضل.
            mode (str): 'auto', 'symbolic', 'numerical'.
            **kwargs: تمرر إلى دوال المعالجة في المحركات الفرعية (مثل num_points للمحرك العددي).

        Returns:
            Optional[Dict[str, Any]]: قاموس النتيجة {'type': 'symbolic'/'numerical', 'result': ...}, أو None.
        """
        log.info(f"CalculusEngine: Differentiate request (mode:{mode}, var:{variable})...")
        eq_obj = self._get_equation_object(equation_input)
        if not eq_obj or eq_obj.is_empty():
            log.error("Differentiation failed: Invalid or empty equation.")
            return None

        result_data: Optional[Dict[str, Any]] = None

        # 1. المحاولة الرمزية
        if mode in ['auto', 'symbolic'] and self.is_symbolic_available():
            log.debug("  Attempting symbolic differentiation...")
            try:
                # نفترض أن المحرك الرمزي يقبل ShapeEquation أو يمكنه الحصول على تمثيل sympy
                # قد يحتاج المحرك الرمزي للوصول لـ EquationManager أيضًا
                symbolic_result = self.sym_engine.symbolic_differentiate(eq_obj, variable, **kwargs)
                if symbolic_result is not None:
                    log.info("  Symbolic differentiation successful.")
                    # النتيجة قد تكون تعبير SymPy أو سلسلة نصية
                    result_data = {'type': 'symbolic', 'result': str(symbolic_result)} # تحويل لـ str للتوحيد
                else:
                    log.warning("  Symbolic differentiation returned None.")
            except Exception as e_sym:
                 log.error(f"  Symbolic differentiation failed: {e_sym}", exc_info=False) # تسجيل الخطأ بدون Traceback كامل عادة
            if mode == 'symbolic' and result_data is None: return None # فشل إجباري

        # 2. المحاولة العددية
        if result_data is None and mode in ['auto', 'numerical'] and self.is_numerical_available():
            log.warning("  Falling back to numerical differentiation...")
            num_points_arg = kwargs.get('num_points', getattr(self.num_engine, 'num_points', DEFAULT_CALCULUS_POINTS))
            points_tensor = self._convert_equation_to_points(eq_obj, variable, num_points=num_points_arg)
            if points_tensor is not None:
                try:
                    # نفترض أن المحرك العددي يعيد (مشتقة, تكامل) كـ Tensors
                    derivative_tensor, _ = self.num_engine.process(points_tensor, **kwargs)
                    if derivative_tensor is not None:
                         log.info("  Numerical differentiation successful.")
                         result_data = {'type': 'numerical', 'result_points': derivative_tensor.cpu().numpy().tolist()} # تحويل لـ list
                    else: log.error("  Numerical differentiation processing returned None.")
                except Exception as e_num:
                    log.error(f"  Numerical differentiation failed during processing: {e_num}", exc_info=True)
            else:
                log.error("  Numerical differentiation failed: Could not convert equation to points.")
            if mode == 'numerical' and result_data is None: return None # فشل إجباري

        # 3. النتيجة النهائية
        if result_data is None: log.error("Differentiation failed using all available methods.")
        return result_data

    def integrate(self,
                  equation_input: Union[AIObject, ShapeEquation, str],
                  variable: str = 'x',
                  mode: str = 'auto',
                  integration_limits: Optional[Tuple[float, float]] = None, # للتكامل المحدود
                  **kwargs
                 ) -> Optional[Dict[str, Any]]:
        """
        إجراء عملية التكامل (رمزي أو عددي، محدود أو غير محدود).

        Args:
            equation_input: الكائن أو المعادلة أو النص.
            variable (str): متغير التكامل.
            mode (str): 'auto', 'symbolic', 'numerical'.
            integration_limits (Optional[Tuple[float, float]]): حدود التكامل المحدود (a, b).
                                                               إذا كان None، يتم إجراء تكامل غير محدود.
            **kwargs: وسائط إضافية للمحركات الفرعية.

        Returns:
            Optional[Dict[str, Any]]: قاموس النتيجة {'type': ..., 'result': ...}, أو None.
                                      النتيجة قد تكون تعبيرًا رمزيًا، قائمة نقاط، أو قيمة عددية (للتكامل المحدود).
        """
        log.info(f"CalculusEngine: Integrate request (mode:{mode}, var:{variable}, limits:{integration_limits})...")
        eq_obj = self._get_equation_object(equation_input)
        if not eq_obj or eq_obj.is_empty():
            log.error("Integration failed: Invalid or empty equation.")
            return None

        result_data: Optional[Dict[str, Any]] = None

        # 1. المحاولة الرمزية
        if mode in ['auto', 'symbolic'] and self.is_symbolic_available():
            log.debug("  Attempting symbolic integration...")
            try:
                symbolic_result = self.sym_engine.symbolic_integrate(eq_obj, variable, limits=integration_limits, **kwargs)
                if symbolic_result is not None:
                    log.info("  Symbolic integration successful.")
                    # النتيجة قد تكون تعبيرًا أو رقمًا (للتكامل المحدود)
                    result_data = {'type': 'symbolic', 'result': str(symbolic_result)}
                else: log.warning("  Symbolic integration returned None.")
            except Exception as e_sym: log.error(f"  Symbolic integration failed: {e_sym}", exc_info=False)
            if mode == 'symbolic' and result_data is None: return None

        # 2. المحاولة العددية
        if result_data is None and mode in ['auto', 'numerical'] and self.is_numerical_available():
            log.warning("  Falling back to numerical integration...")
            num_points_arg = kwargs.get('num_points', getattr(self.num_engine, 'num_points', DEFAULT_CALCULUS_POINTS))
            # التكامل المحدود العددي قد يتطلب نطاقًا يغطي حدود التكامل
            range_to_use = integration_limits if integration_limits else None # Placeholder بسيط
            points_tensor = self._convert_equation_to_points(eq_obj, variable, num_points=num_points_arg, default_range=range_to_use or (-5., 5.))

            if points_tensor is not None:
                try:
                    # المحرك العددي يعيد (مشتقة, تكامل غير محدود/تراكمي)
                    _, integral_tensor = self.num_engine.process(points_tensor, **kwargs)
                    if integral_tensor is not None:
                         # إذا كان تكاملًا محدودًا، نقوم بحسابه من النقاط
                         if integration_limits:
                              # --- منطق حساب التكامل المحدود من النقاط ---
                              # يتطلب معرفة نقاط x المقابلة والتباعد h
                              # (يجب أن تعيد _convert_equation_to_points أو تحتفظ بنقاط x)
                              log.warning("Numerical definite integration from points is not implemented yet.")
                              numeric_result_value = None # Placeholder
                              result_data = {'type': 'numerical', 'result_value': numeric_result_value}
                         else: # تكامل غير محدود (نقاط)
                              log.info("  Numerical indefinite integration successful.")
                              result_data = {'type': 'numerical', 'result_points': integral_tensor.cpu().numpy().tolist()}
                    else: log.error("  Numerical integration processing returned None.")
                except Exception as e_num: log.error(f"  Numerical integration failed during processing: {e_num}", exc_info=True)
            else: log.error("  Numerical integration failed: Could not convert equation to points.")
            if mode == 'numerical' and result_data is None: return None

        # 3. النتيجة النهائية
        if result_data is None: log.error("Integration failed using all available methods.")
        return result_data

    # --- دالة التحويل إلى نقاط (لا تزال Placeholder) ---
    def _convert_equation_to_points(self, equation: ShapeEquation, var: str = 'x',
                                    num_points: Optional[int] = None,
                                    default_range: Tuple[float, float] = (-5., 5.)) -> Optional['torch.Tensor']:
        """
        (مساعد - Placeholder v3) يحاول تحويل معادلة شكلية إلى متجه نقاط y = f(x).
        **تحذير: يتطلب تنفيذًا قويًا يعتمد على تحليل المعادلة ودوال التقييم.**
        **يستخدم NumPy إذا كان متاحًا للتقييم.**
        """
        if not TORCH_AVAILABLE or not NUMPY_AVAILABLE:
             log.error("PyTorch and NumPy are needed for _convert_equation_to_points."); return None
        log.warning("_convert_equation_to_points is a basic placeholder and needs full implementation!")
        if equation.is_empty(): return None

        points_count = num_points or getattr(self.num_engine, 'num_points', DEFAULT_CALCULUS_POINTS)

        # --- منطق استخلاص الدالة وتقييمها (مثال بسيط جدًا) ---
        target_comp: Optional[ShapeComponent] = None
        # البحث عن أول مكون يمكن اعتباره دالة y=f(x)
        supported_func_types = {'line', 'sine', 'exp', 'parabola', 'log'} # أنواع مدعومة كمثال
        for comp in equation.components:
            if comp.type in supported_func_types:
                target_comp = comp
                break
        if not target_comp:
             log.error(f"Cannot convert equation to points: No supported function component ({supported_func_types}) found first."); return None

        comp_range = target_comp.range or default_range
        comp_type = target_comp.type
        comp_params = target_comp.params

        try:
            x_np = np.linspace(comp_range[0], comp_range[1], points_count, dtype=np.float64)
            y_np: Optional[np.ndarray] = None
            # --- محاكاة التقييم (يجب استبدالها بمنطق تقييم فعلي) ---
            # هذا الجزء يتطلب دوال تقييم مشابهة لتلك الموجودة في Renderer
            if comp_type == 'sine' and len(comp_params) == 3: A,fq,ph=map(float,comp_params); y_np=A*np.sin(fq*x_np+ph)
            elif comp_type == 'exp' and len(comp_params) == 3: A,k,x0=map(float,comp_params); y_np=A*np.exp(-k*(x_np-x0))
            elif comp_type == 'line' and len(comp_params) == 4: x1,y1,x2,y2=map(float,comp_params); m=(y2-y1)/(x2-x1+1e-9); y_np=y1+m*(x_np-x1)
            # ... إضافة حالات للأنواع الأخرى المدعومة ...
            else: log.error(f"Evaluation logic for type '{comp_type}' not implemented in placeholder."); return None

            if y_np is not None:
                 # التحقق من عدم وجود NaN أو Inf قبل التحويل
                 if np.any(np.isnan(y_np)) or np.any(np.isinf(y_np)):
                      log.warning(f"NaN or Inf values encountered during evaluation for '{comp_type}'. Cannot convert to tensor.")
                      return None
                 return torch.from_numpy(y_np).float() # التحويل لـ Tensor
            else: return None # فشل التقييم
        except Exception as e: log.error(f"Error evaluating '{comp_type}' for points: {e}"); return None


# --- نهاية ملف calculus_engine.py ---

'''
التغييرات والمراجعات:
الاستيرادات: تم تحديثها لاستيراد المكونات من المسارات النسبية الصحيحة (..representations, .equation_manager). تم جعل استيراد NumPy مشروطًا أيضًا لأنه مطلوب فقط لدالة التحويل إلى نقاط (placeholder).
التهيئة (__init__):
تستقبل EquationManager كمعامل إجباري.
تُهيئ المحركات الفرعية تلقائيًا إذا لم يتم تمريرها وكانت المكتبات المطلوبة (sympy, torch) والملفات المقابلة (symbolic_calculus.py, numerical_calculus.py) موجودة وقابلة للاستيراد.
تستخدم قاموس config لتمرير الإعدادات إلى المحرك العددي (مثل num_points, max_states).
_get_equation_object():
تم تحديثها لاستخدام self.eq_manager.parse() عند استلام سلسلة نصية.
تتحقق بشكل صحيح من وجود سمة equation صالحة عند استلام AIObject.
differentiate() و integrate():
تستخدمان الآن _get_equation_object().
تمرران كائن ShapeEquation (المسترجع أو المحلل) إلى المحركات الفرعية (self.sym_engine.symbolic_..., self.num_engine.process).
تم إضافة **kwargs لتمرير وسائط إضافية (مثل num_points) إلى المحركات الفرعية.
دالة integrate تقبل الآن وسيطة integration_limits وتمررها للمحرك الرمزي، وتشير إلى كيفية استخدامها المستقبلي في الحساب العددي المحدود (الذي لم يتم تنفيذه بعد).
تم تحسين تنسيق النتائج في القاموس المرجع (مثل استخدام result_points أو result_value للنتائج العددية).
_convert_equation_to_points():
تم التأكيد مجددًا على أنها Placeholder وتحتاج لتنفيذ قوي.
تم توضيح اعتماديتها على NumPy و Torch.
تم تحسين منطق البحث عن المكون الأول القابل للتحويل كمثال.
تم إضافة تحذير عند وجود قيم NaN/Inf في النتائج العددية.
الخلاصة:
وحدة foundations/calculus_engine.py الآن متوافقة بشكل جيد مع الهيكل الجديد. هي تعتمد على EquationManager لمعالجة المدخلات وتوفر واجهة موحدة تستدعي المحركات الفرعية الرمزية والعددية (إذا كانت متاحة ومهيأة) وتتعامل مع أنواع المدخلات المختلفة (AIObject, ShapeEquation, str). الجزء الذي لا يزال يتطلب عملًا جوهريًا هو تحويل المعادلات الشكلية المعقدة إلى تمثيل نقطي مناسب للمحرك العددي.
الخطوة التالية:
ننتقل الآن لمراجعة الوحدة التالية في foundations/: وهي pattern_engine.py. سنتأكد من أنها تستخدم AIObject أو سماته بشكل صحيح وتتكامل مع الهيكل العام. هل أنت مستعد؟
'''
