import pytest
from dateutil import parser as datetime_parser

# compare datetime with acceptable time diff in seconds
def is_similar_datetime(v1, v2, max_time_diff=5):
	v1_unix_time = unix_time_from_str(v1)
	v2_unix_time = unix_time_from_str(v2)
	time_diff = abs(v2_unix_time - v1_unix_time)
	return time_diff < max_time_diff

# convert datetime string to unix time
def unix_time_from_str(date_time_str):
	if not isinstance(date_time_str, str):
		raise TypeError("Function unix_time_from_str expects a string")
	return int(datetime_parser.parse(date_time_str).strftime('%s'))

def test_is_similar_datetime_func():
	stime = "2016-05-04T01:29:44.000Z"
	etime = "2016-05-04T01:29:45.000Z"
	assert True == is_similar_datetime(stime, etime)

	etime = "2016-05-04T01:29:43.000Z"
	assert True == is_similar_datetime(stime, etime)

	etime = "2016-05-04T01:29:50.000Z"
	assert False == is_similar_datetime(stime, etime)

	etime = "2016-05-04T01:29:38.000Z"
	assert False == is_similar_datetime(stime, etime)
	assert True == is_similar_datetime(stime, etime, 10)

	with pytest.raises(ValueError):
		etime = "This is not a valid datetime string"
		is_similar_datetime(stime, etime)

	with pytest.raises(TypeError):
		etime = 123
		is_similar_datetime(stime, etime)
