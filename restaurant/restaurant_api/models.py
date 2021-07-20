from django.core.validators import RegexValidator
from django.db import models
from django_countries.fields import CountryField

phone_regex = RegexValidator(
    regex=r'^\+?\d?\d{9,15}$',
    message="Phone number must be entered in the format: '+999999999'. Up to "
            "15 digits allowed."
)


class Person(models.Model):
    """Person."""
    firstname = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    patronymic = models.CharField(max_length=100, verbose_name="father's name",
                                  null=True, blank=True)
    date_of_birth = models.DateField(
        null=True, blank=True, verbose_name='birth date'
    )
    phone = models.CharField(max_length=17, validators=[phone_regex],
                             verbose_name='Contact phone number',
                             null=True, blank=True)

    @property
    def person_name(self):
        return ' '.join((self.surname, self.firstname))

    def __str__(self):
        return self.person_name


class Address(models.Model):
    """Person."""
    country = CountryField()
    province = models.TextField()
    city = models.TextField()
    street = models.TextField()
    house = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=5, null=True, blank=True)

    @property
    def full_address(self):
        return ' '.join((self.country.name, self.province, self.city,
                         self.street, self.house, self.zip_code or ''))

    def __str__(self):
        return self.full_address


class Restaurant(models.Model):
    """Restaurant."""
    # In real life restaurant's name can be not unique, but for my task
    # I've decided to make it unique, because we should update and delete
    # restaurants by name instead id.
    name = models.CharField(max_length=255, verbose_name='Title', unique=True,
                            db_index=True)
    address = models.ForeignKey(
        Address, verbose_name='related address', null=True, blank=True,
        on_delete=models.CASCADE
    )
    phone = models.CharField(max_length=17, validators=[phone_regex],
                             verbose_name='Contact phone number',
                             null=True, blank=True)
    cuisine = models.TextField(null=True, blank=True)
    rating = models.PositiveSmallIntegerField(null=True, blank=True)
    employees = models.ManyToManyField(Person, through='Employee')

    def __str__(self):
        return self.name


class Positions(models.IntegerChoices):
    """PositionsEnumerates."""
    DIRECTOR = 1, 'Director'
    MANAGER = 2, 'Manager'
    COOK = 3, 'Cook'
    WAITER = 4, 'Waiter'


class Employee(models.Model):
    """Restaurant employee."""

    restaurant = models.ForeignKey(
        Restaurant, verbose_name='related restaurant', on_delete=models.CASCADE
    )
    person = models.ForeignKey(Person, verbose_name='related person',
                               on_delete=models.CASCADE)
    position = models.IntegerField(choices=Positions.choices)

    @property
    def position_name(self):
        return self.get_position_display()

    def __str__(self):
        return 'Person {} in restaurant {} in position {} '.format(
            str(self.person), str(self.restaurant), self.position_name
        )

    class Meta:
        # I've decided that one person can take only one position in
        # restaurant. In future I suppose that in model can be added
        # date fields for hiring and firing employee and created check
        # what one person can hold only one position in one restaurant in
        # one time and when can be deleted unique_together option.
        unique_together = ('restaurant', 'person')
