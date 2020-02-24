#!/usr/bin/python

class Policy_Profile:

	def __init__(self):
		self.severity = ''
		self.policy_name = ''
		self.enabled = None
		self.notify_on_black_list = None
		self.behavior = {
			'group_1': [],
			'group_2': []
		}
		self.protocols = []
		self.weekly_schedule = [
			True,
			True,
			True,
			True,
			True,
			True,
			True,
			True
		]
		self.duration_start_percentage = 0
		self.duration_end_percentage = 100
		self.notifying_emails = []

	def set_severity(self, severity):
		if severity not in ['Info', 'Caution', 'Warning', 'Critical']:
			print('Policy_Profile/set_severity: Invalid severity')
			return
		severity_map = {
		    'Info': 'info',
		    'Caution': 'low',
		    'Warning': 'medium',
		    'Critical': 'high'
		}
		self.severity = severity_map[severity]

	def set_policy_name(self, policy_name):
		if type(policy_name) != str:
			print('Policy_Profile/set_policy_name: Policy name is not str')
			return
		self.policy_name = policy_name

	def set_enabled(self, enabled):
		if type(enabled) != bool:
			print('Policy_Profile/set_enabled: Invalid enable state')
			return
		self.enabled = enabled

	def set_notify_on_black_list(self, notify_on_black_list):
		if type(notify_on_black_list) != bool:
			print('Policy_Profile/set_notify_on_black_list: Invalid black list state')
			return
		self.notify_on_black_list = notify_on_black_list

	def set_behavior(self, behavior):
		if type(behavior) != dict:
			print('Policy_Profile/set_behavior: behavior is not dict type')
			return
		if 'group_1' not in behavior or 'group_2' not in behavior:
			print('Policy_Profile/set_behavior: behavior has no group_1 or group_2 key')
			return
		self.behavior = behavior

	def set_protocols(self, protocols):
		if type(protocols) != list:
			print('Policy_Profile/set_protocols: protocols is not list type')
		self.protocols = protocols

	def set_weekly_schedule(self, weekly_schedule):
		if type(weekly_schedule) != list or len(weekly_schedule) != 7:
			print('Policy_Profile/set_weekly_schedule: weekly_schedule is not a valid list')
			return
		self.weekly_schedule = weekly_schedule

	def set_duration_percentages(self, duration_start_percentage, duration_end_percentage):
		if type(duration_start_percentage) != int and type(duration_start_percentage) != float:
			print('Policy_Profile/set_duration_percentages: duration_start_percentage is not float or int')
			return
		if type(duration_end_percentage) != int and type(duration_end_percentage) != float:
			print('Policy_Profile/set_duration_percentages: duration_end_percentage is not float or int')
			return
		if duration_start_percentage > duration_end_percentage:
			print('Policy_Profile/set_duration_percentages: duration_start_percentage is greater that duration_end_percentage')
			return
		self.duration_start_percentage = duration_start_percentage
		self.duration_end_percentage = duration_end_percentage

	def set_notifying_emails(self, notifying_emails):
		if type(notifying_emails) != list:
			print('Policy_Profile/set_notifying_emails: notifying_emails is not list type')
		self.notifying_emails = notifying_emails

	def equal(self, _policy_profile):
		if self.severity != _policy_profile.severity:
			return False
		if self.policy_name != _policy_profile.policy_name:
			return False
		if self.enabled != _policy_profile.enabled:
			return False
		if self.notify_on_black_list != _policy_profile.notify_on_black_list:
			return False
		if self.behavior['group_1'] != _policy_profile.behavior['group_1']:
			return False
		if self.behavior['group_2'] != _policy_profile.behavior['group_2']:
			return False
		if self.protocols != _policy_profile.protocols:
			return False
		if self.weekly_schedule != _policy_profile.weekly_schedule:
			return False
		if self.notifying_emails.sort() != _policy_profile.notifying_emails.sort():
			return False
		return True
