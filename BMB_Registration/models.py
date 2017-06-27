from django.db import models
# from django.contrib.auth.hashers import check_password, set_password
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password


from BMB_Registration.listfield import ListField


TSHIRT_SIZES = (('XS','EXTRA-SMALL'), ('S' , 'SMALL'),
                ('M', 'MEDIUM'), ('L', 'LARGE'),
                ('XL', 'EXTRA-LARGE'), ('XXL', 'XX-LARGE'),
                ('XXXL', 'Vin_Diesel'), ('None','None'))

BOOL         = (('yes', 'yes'), ('no', 'no'))


GENDER       = (('male', 'male'), ('female', 'female'))

PRESENTATION = (('poster', 'poster'), ('talk', 'talk'),
                ('decline', 'decline'))

POSITION     = (('student', 'student'), ('postdoc', 'postdoc'),
                ('faculty', 'faculty'), ('staff', 'staff'))


class PI(models.Model):
    first_name = models.CharField(max_length=30)
    last_name  = models.CharField(max_length=30)

    def __str__(self):
        return '{}, {}'.format(self.last_name, self.first_name)


class Department(models.Model):

    name = models.CharField(max_length=500)

    def __str__(self):
        return '{}'.format(self.name)

class User(models.Model):
    first_name      = models.CharField(max_length=30)
    last_name       = models.CharField(max_length=30)
    gender          = models.CharField(choices=GENDER, max_length=6, default='')
    department      = models.ForeignKey(Department)
    position        = models.CharField(choices=POSITION, max_length=7, default='')
    password        = models.CharField(max_length=100)
    email           = models.EmailField(blank=False, unique=True)
    date_registered = models.DateTimeField(auto_now_add=True)
    lab             = models.ForeignKey(PI, blank=True)
    shirt_size      = models.CharField(choices=TSHIRT_SIZES, max_length=4)
    presentation    = models.CharField(choices=PRESENTATION, default='decline', max_length=7, help_text='Years 3 and above must present a poster.')
    funding_source  = models.CharField(max_length=10)
    stay_at_hotel   = models.CharField(choices=BOOL, default='yes', max_length=3)
    share_room      = models.CharField(choices=BOOL, default='yes', max_length=3)
    roommate_pref   = models.CharField(max_length=100, blank=True)
    vegetarian      = models.CharField(choices=BOOL, default='no', max_length=3)


    list_display =  ('last_name', 'first_name', 'gender',
                     'department', 'lab', 'position', 'email',
                     'date_registered', 'shirt_size', 'presentation',
                     'funding_source', 'stay_at_hotel', 'share_room',
                     'roommate_pref', 'vegetarian'
                    )
    class Meta:
        ordering = ('last_name', 'first_name')

    def __str__(self):
        return '{}, {}'.format(self.last_name, self.first_name)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """
        Returns a boolean of whether the raw_password was correct. Handles
        hashing formats behind the scenes.
        """
        def setter(raw_password):
            self.set_password(raw_password)
            self.save(update_fields=["password"])
        return check_password(raw_password, self.password, setter)



class Variable(models.Model):
    variable_name  = models.CharField(max_length=50)
    variable_value = models.CharField(max_length=300)


    def __str__(self):
        return '%s = %s' % (self.variable_name, self.variable_value)

# class SeparatedValuesField(models.TextField):

#     def __init__(self, *args, **kwargs):
#         self.token = kwargs.pop('token', ',')
#         super(SeparatedValuesField, self).__init__(*args, **kwargs)

#     def to_python(self, value):
#         if not value: return
#         if isinstance(value, list):
#             return value
#         return value.split(self.token)

#     def from_db_value(self, value, expression, connection, context):
#         pass


#     def get_db_prep_value(self, value):
#         if not value: return
#         assert(isinstance(value, list) or isinstance(value, tuple))
#         return self.token.join([unicode(s) for s in value])

#     def value_to_string(self, obj):
#         value = self._get_val_from_obj(obj)
#         return self.get_db_prep_value(value)

class Submission(models.Model):

    user          = models.ForeignKey(User)
    title         = models.CharField(max_length=500)
    authors       = models.CharField(max_length=500, blank=True, default='')
    PI            = models.ForeignKey(PI, blank=True, null=True)
    abstract      = models.TextField(max_length=(8*300))
    poster_number = models.IntegerField(blank=True, null=True)
    scores        = models.CharField(blank=True, null=True, max_length=30)

    list_display  = ('user', 'title', 'authors', 'PI', 'poster_number')

    def __str__(self):
        return '{}\n{} {}'.format(self.title, self.user, self.authors)
