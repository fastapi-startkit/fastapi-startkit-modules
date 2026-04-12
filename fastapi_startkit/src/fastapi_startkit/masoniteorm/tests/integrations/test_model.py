# TODO
# test case 1
# only the properties defined in the model class are fillables
# can use Guard __guarded__ to prevent fillable

# test case 2: Test tables names, primary_id, database Connections timestamp etc,
# give default value example
# class User:
#    status: Status = Status.Pending
#

# test cases 3:
# model retrivuve
# await User.query().get()
# await User.query().where('status').get()
# Sub queries
# use App\Models\Destination;
# use App\Models\Flight;
#  example similar in python
# return Destination::addSelect(['last_flight' => Flight::select('name')
#     ->whereColumn('destination_id', 'destinations.id')
#     ->orderByDesc('arrived_at')
#     ->limit(1)
# ])->get();



# ## Creation methods
# use App\Models\Flight;
#
# // Retrieve flight by name or create it if it doesn't exist...
# $flight = Flight::firstOrCreate([
#     'name' => 'London to Paris'
# ]);
#
# // Retrieve flight by name or create it with the name, delayed, and arrival_time attributes...
# $flight = Flight::firstOrCreate(
#     ['name' => 'London to Paris'],
# ['delayed' => 1, 'arrival_time' => '11:30']
# );
#
# // Retrieve flight by name or instantiate a new Flight instance...
# $flight = Flight::firstOrNew([
#     'name' => 'London to Paris'
# ]);
#
# // Retrieve flight by name or instantiate with the name, delayed, and arrival_time attributes...
# $flight = Flight::firstOrNew(
#     ['name' => 'Tokyo to Sydney'],
# ['delayed' => 1, 'arrival_time' => '11:30']
# );
