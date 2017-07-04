from django.contrib import admin
from django.utils.translation import ugettext_lazy as _


class ValueRangeFilter(admin.FieldListFilter):
    def __init__(self, field, *args, **kwargs):
        self.lookup_kwarg = '%s__range' % kwargs['field_path']
        self.lookup_choices = getattr(field, 'list_lookup_range', (
            # default range options
            (None, _('All')),
            ([0, 100], '0-100'),
            ([100, 300], '100-300'),
            ([300, 1000], '300-1000'),
            ([1000, 10000], '1000-10000'),
            ([10000, None], '10000+'),
        ))
        super(ValueRangeFilter, self).__init__(field, *args, **kwargs)

    def expected_parameters(self):
        return [self.lookup_kwarg]

    def get_value_range(self):
        if not self.used_parameters.get(self.lookup_kwarg):
            return None
        return [int(n.strip("' ")) if n.strip("' ") != 'None' else None
                for n in self.used_parameters[self.lookup_kwarg].strip(
                    '[]').split(',')]

    def choices(self, cl):
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.get_value_range() == lookup,
                'query_string': cl.get_query_string({
                    self.lookup_kwarg: lookup,
                }, []),
                'display': title,
            }

    def queryset(self, request, queryset):
        if not self.used_parameters:
            return queryset
        values_range = self.get_value_range()
        if not values_range:
            return queryset
        min_val, max_val = values_range
        if min_val and max_val:
            query = {'%s__range' % self.field_path:
                     (min_val, max_val)}
        elif min_val:
            query = {'%s__gt' % self.field_path: min_val}
        elif max_val:
            query = {'%s__lt' % self.field_path: max_val}
        else:
            query = {}
        return queryset.filter(**query)
