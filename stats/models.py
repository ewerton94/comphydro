from django.db import models
from django.utils.translation import gettext_lazy as _
from data.models import Discretization,OriginalSerie,TemporalSerie

class Reduction(models.Model):
    type = models.CharField(max_length=20,verbose_name = _('type'))
    class Meta:
        verbose_name_plural = _("Reductions")
        verbose_name = _("Reduction")
    def __str__(self):
        return '%s'%self.type
    
    
class ReducedSerie(models.Model):
    original_serie = models.ForeignKey(OriginalSerie,verbose_name = _('original serie'))
    discretization = models.ForeignKey(Discretization,verbose_name = _('discretization'))
    reduction = models.ForeignKey(Reduction,verbose_name = _('reduction'))
    temporal_serie_id = models.IntegerField(verbose_name = _('temporal serie id'))
    class Meta:
        verbose_name_plural = _("Reduced Series")
        verbose_name = _("Reduced Serie")
    def __str__(self):
        return _('%(discretization)s %(reduction)s Serie from %(station)s station')%{'reduction':self.reduction.type,
                                                                                     'discretization':self.discretization.type,
                                                                                     'station':self.original_serie.station}
    
    
class RollingMeanSerie(models.Model):
    serie_original = models.ForeignKey(OriginalSerie,verbose_name = _('original serie'))
    temporal_serie_id = models.IntegerField(verbose_name = _('temporal serie id'))
    discretization = models.ForeignKey(Discretization,verbose_name = _('discretization'))
    class Meta:
        verbose_name_plural = _("Rolling mean series")
        verbose_name = _("Rolling mean serie")
    def __str__(self):
        return _('%s Serie')%(self.discretization)
