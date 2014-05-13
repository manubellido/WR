import sys
from datetime import datetime
from simulation.models import SimulationInfo
from generate_users import UserGenerator
from generate_friendship import FriendshipGenerator
from generate_circuits import CircuitGenerator
from generate_categories_follow import CategoryFollowGenerator
from generate_places import PlaceGenerator
from generate_ratings import RatingsGenerator
from generate_follows import FollowGenerator
from generate_topics import TopicGenerator
from generate_visits import VisitGenerator
from generate_places_done import PlaceDoneGenerator
from generate_explicit_interest import ExplicitGenerator
from generate_topic_circuit import Topic_circuit_generator
from generate_place_circuit import Place_circuit_generator
from clint.textui import colored
    

# ----------------------------- F U N C T I O N S ------------------------------

def Delete():
    pass

def Build():
    try:
        year = int(sys.argv[4])
        month = int(sys.argv[5])
        day = int(sys.argv[6])
        timestamp = datetime(year, month, day)
    except IndexError:
        print colored.red("Date missing: python main.py build yyyy mm dd")
        print colored.yellow("Asumming current date:")
        timestamp = datetime.today()
    
    print "BUILDING Database and content"
    # Generate Users
    #user_generator = UserGenerator()
    #user_generator.run()
    # Generate Places
    #place_generator = PlaceGenerator()
    #place_generator.run()

    # Generate Friendships
    #fs_generator = FriendshipGenerator()
    #fs_generator.run()

    # Generate Topics
    #tp_generator = TopicGenerator(amount=1000)
    #tp_generator.run()

    # Generate Circuits
    #circuit_generator = CircuitGenerator()
    #circuit_generator.run()
    # Generate places per circuit
    #pl_ct_generator = Place_circuit_generator()
    #pl_ct_generator.run()
    # Generate topics per circuit
    #tc_ct_generator = Topic_circuit_generator()
    #tc_ct_generator.run()

    # Generate explicit_interests
    #exp_generator = ExplicitGenerator(date=timestamp)
    #exp_generator.run()

    # Generate Visits
    #visit_generator = VisitGenerator(date=timestamp)
    #visit_generator.run(min_equiv=360) # 360 mins = 6 hours

    # Generate topic follows
    #follow_generator = FollowGenerator(date=timestamp) 
    #follow_generator.run()

    # Generate Ratings
    #rating_generator = RatingsGenerator()
    #rating_generator.run()

    # Generate category follow
    #category_follow = CategoryFollowGenerator()
    #category_follow.run()

    # Generate Place.done
    pc_done = PlaceDoneGenerator()
    pc_done.run()

    # SAVE SIMULATION TIMESTAMP
    #init_info = SimulationInfo(date=timestamp)
    #init_info.save()

def Simulate():
    try:
        ndays = int(sys.argv[4])
    except IndexError:
        print colored.red("Number of days missing missing: python main.py simulate [ndays]")
        print colored.yellow("Asumming 1 day simulation:")
        ndays = 1

    for i in ndays:
        print colored.cyan("Simulating day "),
        print colored.cyan(i)
 
        # Simulate Users
        #user_generator = UserGenerator(session=session, names_file='names.txt')
        #new_usrs = user_generator.simulate()

        # Simulate Circuits
        #circuit_generator = CircuitGenerator(session=session, engine=ENGINE)
        #new_circuits = circuit_generator.run(new_users=new_usrs)

        # Generate places per circuit
        #pl_ct_generator = Place_circuit_generator(session=session, engine=ENGINE)
        #pl_ct_generator.run(new_circuits=new_circuits)

        # Generate topics per circuit
        #tc_ct_generator = Topic_circuit_generator(session=session, engine=ENGINE)
        #tc_ct_generator.run(new_circuits=new_circuits)

        #sim = Simulation_info()
        #last_date = sim.Get_last_date(session=session)
        #actual_date = last_date + timedelta(days=1)

        # Simulate Visits
        #visit_generator = VisitGenerator(session=session, engine=ENGINE, date=actual_date)
        #visit_generator.run(min_equiv=360) # 360 mins = 6 hours
    
        # Generate topic follows
        #follow_generator = FollowGenerator(session=session, engine=ENGINE, date=actual_date) 
        #follow_generator.run(new_users=new_usrs)

        #sim.date = actual_date
        #session.add(sim)
        #session.commit()

"""
ARGV options: delete = erase entire DB
            : build yyyy mm dd = builds the hole DB and populates tables based on yyyy mm dd
            : rebuild yyyy mm dd = delete + build
            : simulate ndays = simulates a day, if ndays passed, simulates n number of days
            : simulate_until yyyy mm dd = simulates until given date
"""

def run():

    try:
        option = sys.argv[3].upper()
    except IndexError:
        print colored.red("Argument missing: python main.py delete|build yyyy mm dd|simulate ndays|rebuild yyyy mm dd")
        exit(0)

    if option == 'DELETE':
        #Delete()
        exit(0)

    if option == 'BUILD':
        Build()
        exit(0)

    if option == 'SIMULATE':
        #Simulate()
        exit(0)

    if option == 'REBUILD':
        """
        DETELE + BUILD
        """
        #Delete()
        #Build()
        exit(0)

    else:
        print "Not an option: python main.py build|delete|simulate"
        exit(0)
    
