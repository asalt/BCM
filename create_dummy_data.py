import random

from BCM import wsgi
from BMB_Registration.models import User, Submission, Department, PI
from BMB_Registration.models import BOOL, GENDER, PRESENTATION, POSITION, TSHIRT_SIZES

def main():

    male_first_names  = [
                'JAMES', 'JOHN', 'ROBERT', 'MICHAEL', 'WILLIAM', 'DAVID', 'RICHARD', 'CHARLES',
                'JOSEPH', 'THOMAS', 'CHRISTOPHER', 'DANIEL', 'PAUL', 'MARK', 'DONALD', 'GEORGE',
                'KENNETH', 'STEVEN', 'EDWARD', 'BRIAN', 'RONALD', 'ANTHONY', 'KEVIN', 'JASON',
                'MATTHEW', 'GARY', 'TIMOTHY', 'JOSE', 'LARRY', 'JEFFREY', 'FRANK', 'SCOTT',
                'ERIC', 'STEPHEN', 'ANDREW', 'RAYMOND', 'GREGORY', 'JOSHUA', 'JERRY', 'DENNIS',
                'WALTER', 'PATRICK', 'PETER', 'HAROLD', 'DOUGLAS', 'HENRY', 'CARL', 'ARTHUR',
                'RYAN', 'ROGER',
            ]


    female_first_names = [
                        'MARY',  'PATRICIA',  'LINDA',  'BARBARA',  'ELIZABETH',
                        'JENNIFER',  'MARIA',  'SUSAN',  'MARGARET',  'DOROTHY',
                        'LISA',  'NANCY',  'KAREN',  'BETTY',  'HELEN',  'SANDRA',
                        'DONNA',  'CAROL',  'RUTH',  'SHARON',  'MICHELLE',  'LAURA',
                        'SARAH',  'KIMBERLY',  'DEBORAH',  'JESSICA',  'SHIRLEY',
                        'CYNTHIA',  'ANGELA',  'MELISSA',  'BRENDA',  'AMY',  'ANNA',
                        'REBECCA',  'VIRGINIA',  'KATHLEEN',  'PAMELA',  'MARTHA',
                        'DEBRA',  'AMANDA',  'STEPHANIE',  'CAROLYN',  'CHRISTINE',
                        'MARIE',  'JANET',  'CATHERINE',  'FRANCES',  'ANN',
                        'JOYCE',  'DIANE',
                        ]

    last_names = [
                        'SMITH', 'JOHNSON', 'WILLIAMS', 'BROWN', 'JONES', 'MILLER',
                        'DAVIS', 'GARCIA', 'RODRIGUEZ', 'WILSON', 'MARTINEZ', 'ANDERSON',
                        'TAYLOR', 'THOMAS', 'HERNANDEZ', 'MOORE', 'MARTIN', 'JACKSON',
                        'THOMPSON', 'WHITE', 'LOPEZ', 'LEE', 'GONZALEZ', 'HARRIS', 'CLARK',
                        'LEWIS', 'ROBINSON', 'WALKER', 'PEREZ', 'HALL', 'YOUNG', 'ALLEN',
                        'SANCHEZ', 'WRIGHT', 'KING', 'SCOTT', 'GREEN', 'BAKER', 'ADAMS',
                        'NELSON', 'HILL', 'RAMIREZ', 'CAMPBELL', 'MITCHELL', 'ROBERTS',
                        'CARTER', 'PHILLIPS', 'EVANS', 'TURNER', 'TORRES', 'PARKER',
                        'COLLINS', 'EDWARDS', 'STEWART', 'FLORES', 'MORRIS', 'NGUYEN',
                ]


    title = 'Lorem Ipsum'

    authors = 'X, Y, Z'

    lorem_ipsum = (' Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer nec odio. Praesent libero. Sed'
    ' cursus ante dapibus diam. Sed nisi. Nulla quis sem at nibh elementum imperdiet. Duis sagittis'
    ' ipsum. Praesent mauris. Fusce nec tellus sed augue semper porta. Mauris massa. Vestibulum'
    ' lacinia arcu eget nulla. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per'
    ' inceptos himenaeos. Curabitur sodales ligula in libero. Sed dignissim lacinia nunc. Curabitur'
    ' tortor. Pellentesque nibh. Aenean quam. In scelerisque sem at dolor. Maecenas mattis. Sed'
    ' convallis tristique sem. Proin ut ligula vel nunc egestas porttitor. Morbi lectus risus, iaculis'
    ' vel, suscipit quis, luctus non, massa. Fusce ac turpis quis ligula lacinia aliquet. Mauris'
    ' ipsum. Nulla metus metus, ullamcorper vel, tincidunt sed, euismod in, nibh. Quisque volutpat'
    ' condimentum velit. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per'
    ' inceptos himenaeos. Nam nec ante. Sed lacinia, urna non tincidunt mattis, tortor neque'
    ' adipiscing diam, a cursus ipsum ante quis turpis. Nulla facilisi. Ut fringilla. Suspendisse'
    ' potenti. Nunc feugiat mi a tellus consequat imperdiet. Vestibulum sapien. Proin quam. Etiam'
    ' ultrices. Suspendisse in justo eu magna luctus suscipit. Sed lectus. Integer euismod lacus'
    ' luctus magna. Quisque cursus, metus vitae pharetra auctor, sem massa mattis sem, at interdum'
    ' magna augue eget diam. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere'
    ' cubilia Curae; Morbi lacinia molestie dui. Praesent blandit dolor. Sed non quam. In vel mi sit'
    ' amet augue congue elementum. Morbi in ipsum sit amet pede facilisis laoreet. Donec lacus nunc,'
    ' viverra nec, blandit vel, egestas et, augue. Vestibulum tincidunt malesuada tellus. Ut ultrices'
    ' ultrices enim. Curabitur sit amet mauris. Morbi in dui quis est pulvinar ullamcorper. Nulla'
    ' facilisi. Integer lacinia sollicitudin massa. Cras metus. Sed aliquet risus a tortor. Integer id'
    ' quam. Morbi mi. Quisque nisl felis, venenatis tristique, dignissim in, ultrices sit amet, augue.'
    ' Proin sodales libero eget ante. Nulla quam. Aenean laoreet. Vestibulum nisi lectus, commodo ac,'
    ' facilisis ac, ultricies eu, pede. Ut orci risus, accumsan porttitor, cursus quis, aliquet eget,'
    ' justo. Sed pretium blandit orci. Ut eu diam at pede suscipit sodales. Aenean lectus elit,'
    ' fermentum non, convallis id, sagittis at, neque. Nullam mauris orci, aliquet et, iaculis et,'
    ' viverra vitae, ligula. Nulla ut felis in purus aliquam imperdiet. Maecenas aliquet mollis'
    ' lectus. Vivamus consectetuer risus et tortor. Lorem ipsum dolor sit amet, consectetur adipiscing'
    ' elit. Integer nec odio. Praesent libero. Sed cursus ante dapibus diam. Sed nisi. Nulla quis sem'
    ' at nibh elementum imperdiet. Duis sagittis ipsum. Praesent mauris. Fusce nec tellus sed augue'
    ' semper porta. Mauris massa. Vestibulum lacinia arcu eget nulla. Class aptent taciti sociosqu ad'
    ' litora torquent per conubia nostra, per inceptos himenaeos. Curabitur sodales ligula in libero.'
    ' Sed dignissim lacinia nunc. Curabitur tortor. Pellentesque nibh. Aenean quam. In scelerisque sem'
    ' at dolor. Maecenas mattis. Sed convallis tristique sem. Proin ut ligula vel nunc egestas'
    ' porttitor. Morbi lectus risus, iaculis vel, suscipit quis, luctus non, massa. Fusce ac turpis'
    ' quis ligula lacinia aliquet. Mauris ipsum. Nulla metus metus, ullamcorper vel, tincidunt sed,'
    ' euismod in, nibh. Quisque volutpat condimentum velit. Class aptent taciti sociosqu ad litora'
    ' torquent per conubia nostra, per inceptos himenaeos. Nam nec ante. Sed lacinia, urna non'
    ' tincidunt mattis, tortor neque adipiscing diam, a cursus ipsum ante quis turpis. Nulla facilisi.'
    ' Ut fringilla. ')

    abstract_sentances = [x+'.' for x in lorem_ipsum.split('.')]

    PIs = ['Nobel, Alfred', 'Netwon, Issac', 'Galilei, Galileo',
           'Pasteur, Louis', 'Tesla, Nikola', 'Franklin, Rosalind',
           'da Vinci, Leonardo', 'Sagan, Carl']

    dept, created = Department.objects.get_or_create(name='BMB')
    if created:
        print('Created', dept)

    for pi in PIs:
        split = pi.split(',')
        last  = split[0].strip()
        first = split[1].strip()
        pi, created = PI.objects.get_or_create(last_name=last, first_name=first)
        if created:
            print('Created', pi)

    print('Generating user data...', flush=True)

    for i in range(100):

        gender        = random.choice(GENDER)[0]

        first_name    = random.choice(male_first_names if gender == 'male' else female_first_names)
        last_name     = random.choice(last_names)

        presentation  = random.choice(PRESENTATION)[0]
        position      = random.choice(POSITION)[0]
        tshirt_size   = random.choice(TSHIRT_SIZES)[0]
        stay_at_hotel = random.choice(BOOL)[0]
        share_room    = random.choice(BOOL)[0]
        vegetarian    = random.choice(BOOL)[0]

        department = Department.objects.order_by('?').first()
        lab = PI.objects.order_by('?').first()

        funding_source = '1234567890'

        email = ''.join([chr(x) for x in [random.randint(97, 122) for y in range(15)]])
        email += '@abc.com'

        user = User.objects.create(first_name=first_name, last_name=last_name, gender=gender,
                                   presentation=presentation, position=position, shirt_size=tshirt_size,
                                   funding_source=funding_source, stay_at_hotel=stay_at_hotel,
                                   share_room=share_room, vegetarian=vegetarian, lab=lab,
                                   department=department, email=email)


        if not presentation == 'decline':

            abstract = ''.join([random.choice(abstract_sentances) for _ in range(random.randint(20,30))])
            Submission.objects.create(title=title, authors=authors,
                                      final_author=lab,
                                      presenter='{} {}'.format(first_name, last_name),
                                      abstract=abstract, PI=lab, user=user)

    print(' .done', flush=True)
    return

if __name__ == '__main__':
    main()
