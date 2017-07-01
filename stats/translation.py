from modeltranslation.translator import translator, TranslationOptions
from .models import Reduction,ReducedSerie,RollingMeanSerie

class ReductionTranslationOptions(TranslationOptions):
    fields = ('type',)
    
    


translator.register(Reduction, ReductionTranslationOptions)