#!/usr/bin/python

#######################################################################################
#  Author : Vinh Nguyen
#    Date : 4/11/17
#######################################################################################

import pdb, json, sys, os, re, subprocess, numpy
from jtl import create_parser
from collections import Counter
from zb_logging import logger as logging


class zbJmeter():

	def __init__(self):
		pass

	def run(self, **kwargs):
		commandList = ['-n', '-t', kwargs["jmeterprofile"], '-l', kwargs["log"], kwargs["options"], '-Jjmeter.save.saveservice.url=true', '-Jjmeter.save.saveservice.output_format=xml', '-Jjmeter.save.saveservice.thread_counts=true']

		# set command if hostname is zbat00X
		if 'zbat00' in os.uname()[1]:
			commandList.insert(0, 'sudo')
			commandList.insert(1, '$JMETER_HOME/bin/jmeter')
		else:
			commandList.insert(0, 'jmeter')

		print(' '.join(commandList))
		
		output = os.popen(' '.join(commandList)).readlines()
		#proc = subprocess.Popen(commandList, stdout=subprocess.PIPE)
		#(output,err) = proc.communicate()
		
		return output


	def run_tps(self, jconfig, jendpoint, jheader_params):
		commandList = ['-n', '-t', jconfig["jmeter_jmx"], '-l', jconfig["jmeter_log"], jconfig["options"], jendpoint, jheader_params.replace(" ","")]

		# set command if hostname is zbat00X
		if 'zbat00' in os.uname()[1]:
			commandList.insert(0, 'sudo')
			commandList.insert(1, '$JMETER_HOME/bin/jmeter')
		else:
			commandList.insert(0, 'jmeter')

		print(' '.join(commandList))

		output = os.popen(' '.join(commandList)).readlines()

		#output = os.popen("jmeter -n -t /home/kevinip/zbat/3p/jmeter/kev_tps.jmx -l /home/kevinip/zbat/3p/jmeter/log/dashboard/series_jmeterlog_1550051972.jtl -Jtpsfile=/home/kevinip/zbat/3p/jmeter/log/tps.jtl").readlines()
		#proc = subprocess.Popen(commandList, stdout=subprocess.PIPE)
		#(output,err) = proc.communicate()

		return output


	def parseXmlLog(self, logfilepath):
		parser = create_parser(logfilepath)
		return parser


	def checkFail(self, sampleobj, **kwargs):
		for sample in sampleobj.itersamples():
			result = {'pass':True, 'messages':[]}

			if sample.response_code != '200':
				result['pass'] = False
				result['messages'].append('HTTP Response not 200')
				
			if sample.response_message != 'OK':
				result['pass'] = False
				result['messages'].append('HTTP Response Code not OK')
			
			if 'maxLatency' in kwargs:
				latency = sample.latency_time.total_seconds()
				baseline = float(kwargs['maxLatency'])
				if latency > baseline:
					result['pass'] = False
					message = 'Latency %s exceed baseline %s.' % (str(latency), str(baseline))
					result['messages'].append(message)
			
			for i in range(len(sample.assertion_results)):
				if sample.assertion_results[i].failure == True:
					result['pass'] = False
					message = sample.assertion_results[i].name+': '+sample.assertion_results[i].failure_message
					result['messages'].append(message)
			
			if len(result['messages']) > 0: result['log'] = str(sample)

			yield result


	def parseOutput(self, output):
		results = {}
		if type(output) == str:
			output = output.splitlines()

		counter = 0
		for i in output:
			#m = re.match(r"(summary +    (.*)Avg:   (.*)Max:  (.*)Err:     (.*) \((.*)\)", i)
			m = re.match(r"summary(.*)Avg:(.*)Min:(.*)Max:(.*)Err:(.*)", i)
			if(m):
				# look for transaction result
				r = m.group(1).replace(' ','')
				rf = re.match(r"([+=]*)(.*)in(.*)=(.*)/(.*)", r)
				if(rf):
					total = rf.group(2)
					rate = rf.group(4)
				# look for error 
				e = m.group(5).replace(' ','')
				ef = re.match(r"(\d+)\((.*)%\)(.*)", e)
				if(ef):
					error = ef.group(1)
					errpercent = ef.group(2)
				# look for latency
				aveLatency = m.group(2).replace(' ','')
				minLatency = m.group(3).replace(' ','')
				maxLatency = m.group(4).replace(' ','')

				results[str(counter)] = {
											"total": total, 
											"rate": rate, 
											"aveLatency": aveLatency, 
											"minLatency": minLatency, 
											"maxLatency": maxLatency,
											"error": error,
											"errpercent": errpercent
										}
				counter+=1
		return results


	def parse_tps(self, api_endpoint, jmeter_tps_file):
		""" Returns successful tps values --> key(time):value(tps) pair(s) """
		current_sample = []
		responses = []
		times = {}
		end_times = []

		line_count = 0
		success_count = 0
		failure_count = 0
		trailing_failure_count = 0

		with open(jmeter_tps_file, "r") as tps_data: # Opens .jtl file generated from JMeter, will close when done
			lines = tps_data.readlines()

		for line in lines: # Parsing the file
			line_count += 1
			current_sample.append(line) # Adds all lines to 'current_sample' list
			end_of_sample = re.match(r'</httpSample>', line)
			
			if end_of_sample:
				for sample_line in current_sample: # Loops through 'current_sample'
					
					# Block records ending times of successful responses
					response_success = re.search(r'rc=\"200\"', sample_line)
					if response_success:
						times["elapsed_time"] = int(re.search(r't=\"(\d+)\"', sample_line).group(1))
						times["timestamp"] = int(re.search(r'ts=\"(\d+)\"', sample_line).group(1))
						times["end_time"] = times["elapsed_time"] + times["timestamp"]
						end_times.append(times["end_time"])
						responses.append("Success")
						success_count += 1
						if success_count == 1:
							start_time = times["timestamp"]
						continue

					# Block records ending times of 'Non HTTP' failure responses
					response_failure_message = re.search(r'(?<=rm=\")Non HTTP.*(?=\")', sample_line)
					if response_failure_message:
						logging.info("API Endpoint: {}, Response Failure Message: {}".format(api_endpoint, response_failure_message.group()))
						responses.append("FAIL")
						failure_count += 1
						break

					# Block records ending times of failed duration assertion or failed size assertion responses
					assertion_failure_message = re.search(r'(?<=<failureMessage>).*(?=</failureMessage>)', sample_line)
					if assertion_failure_message:
						logging.info("API Endpoint: {}, Assertion Failure Message: {}".format(api_endpoint, assertion_failure_message.group()))
						del end_times[-1]  # Need to delete last element in 'end_times' list, counted as success due to 'rc=200' but fails assertion in JMeter 
						del responses[-1]  # Need to delete last element in 'responses' list, counted as success due to 'rc=200' but fails assertion in JMeter
						success_count -= 1 # Need to subtract 1, because increased count as success
						responses.append("FAIL")
						failure_count += 1
						break

				current_sample = [] # Clears 'current_sample' after obtaining data from list
		
		# Counts trailing failures at the end of a test, should be subtracted from 'success_rate' calculation
		for response in reversed(responses):
			if response == "FAIL":
				trailing_failure_count += 1
			else:
				break

		success_cutoff = 0.97
		success_rate = round(((success_count) / float(success_count + failure_count - trailing_failure_count)),3)
		
		print(("\nThe Success Cutoff is: {}%".format(success_cutoff * 100)))
		print(("Number of TPS Successes: {}".format(success_count)))
		print(("Number of TPS Failures: {}".format(failure_count)))
		print(("TPS Success Rate: {}%".format(success_rate * 100)))

		logging.info("The Success Cutoff is: {}%".format(success_cutoff * 100))
		logging.info("Number of TPS Successes: {}".format(success_count))
		logging.info("Number of TPS Failures: {}".format(failure_count))
		logging.info("TPS Success Rate: {}%".format(success_rate * 100))

		tps_times = [x - start_time + 500 for x in end_times] # '500' accounts for lag, matches transactions per second graph in JMeter

		tps_times_sec = [x / 1000 for x in tps_times] # tps times in seconds

		tps_dict = Counter(tps_times_sec) # Counts transaction(s) for the time (in seconds), {'time': '# of transaction(s)'}

		logging.info("Transactions per second dictionary, 'occurence time: value': {}".format(tps_dict))
		
		return tps_dict if success_rate >= success_cutoff else False, \
		logging.error("The success rate calculated '{}%' should be greater or equal to the cutoff '{}%'".format(success_rate * 100,success_cutoff * 100))


	def maximum_tps(self, tps_dict):
		""" Returns the maximum tps value(s) --> key(time):value(tps) pair(s) """
		max_tps_value = max(tps_dict[0].values()) # Finds the max # of tps among all times

		max_tps_dict = [x for x in list(tps_dict[0].items()) if x[1] == max_tps_value] # Filters for items with max # of tps , {'time': '# of transactions')

		logging.info("Maximum transactions per second, 'occurence time: value': {}".format(max_tps_dict))

		return max_tps_dict


	def average_upper_tps(self, tps_dict):
		""" Returns the average of the upper bounded tps values """
		tps_values = [x[1] for x in list(tps_dict[0].items())] # Extract the tps values only, no times associated

		tps_values_arr = numpy.array(tps_values) # Convert to numpy array

		mean = numpy.mean(tps_values_arr, axis=0) # Use numpy to find the mean
		
		std_dev = numpy.std(tps_values_arr, axis=0) # Use numpy to find the standard deviation

		tps_filtered = [x for x in tps_values if (x < mean + 2 * std_dev)] # Filters out tps upperbound outliers (over 2 std dev, > 97%) 

		upper_tps_value = numpy.percentile(list(map(int,  tps_filtered)), 70) # Obtains top 70% of filtered tps values without upperbound outliers

		avg_upper_tps = numpy.mean([x for x in tps_filtered if (x >= upper_tps_value)]).round(3) # Mean of upper values, rounded to 3 decimal places

		logging.info("Average upper-bounded transactions per second: {}".format(avg_upper_tps))

		return avg_upper_tps
