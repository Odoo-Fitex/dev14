# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime as dt, date
from time import time
import datetime
import pytz
from pytz import timezone
from odoo.exceptions import ValidationError, AccessError, MissingError, UserError


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    late = fields.Float(string='Late', compute='', store=True, readonly=True)
    over_time = fields.Float(string='Over Time')
    early_sign_in = fields.Float(string='Early Sign In')
    early_leave = fields.Float(string='Early Leave')
    # colored = fields.Boolean(string="is_colored", default=False)

    def colored_method(self):
        print("Hi Colored")
        for rec in self:
            if rec.check_in and rec.check_out:
                check_in = rec.check_in
                user_tz = rec.env.context.get('tz')
                real_date = pytz.UTC.localize(check_in).astimezone(timezone(user_tz)).replace(tzinfo=None)
                check_in_as_date = dt.strptime(str(real_date), '%Y-%m-%d %H:%M:%S').date()

                check_out = rec.check_out
                # user_tz = rec.env.context.get('tz')
                real_date = pytz.UTC.localize(check_out).astimezone(timezone(user_tz)).replace(tzinfo=None)
                check_out_as_date = dt.strptime(str(real_date), '%Y-%m-%d %H:%M:%S').date()
                if check_out_as_date > check_in_as_date:
                    # print("sign_out is bigger than Sign_in")
                    rec.colored = True
                else:
                    rec.colored = False
            else:
                rec.colored = False

    # def compute_fields(self):
    #     t = self.check_in
    #     t = dt.strptime(str(t), '%Y-%m-%d %H:%M:%S')
    #     print(t.strftime('%H:%M:%S'))
    #     t_string_time = t.strftime('%H:%M:%S')
    #     t_time = dt.strptime(str(t_string_time), '%H:%M:%S').time()
    #     hour_1 = datetime.time(16,0,0)
    #     total = dt.combine(date.today(), t_time) - dt.combine(date.today(), hour_1)
    #     # total = t_time - hour_1
    #     print("Total = ", total)

    def compute_fields(self):
        t = self.check_in
        t = dt.strptime(str(t), '%Y-%m-%d %H:%M:%S')
        hour = t.hour
        print("hour = ", hour)
        if hour == 6:
            print("YESSSSSS")
        print(t.strftime('%H:%M:%S'))
        t_string_time = t.strftime('%H:%M:%S')
        t_time = dt.strptime(str(t_string_time), '%H:%M:%S').time()
        x = dt(1988, 2, 19, 6, 0, 0)
        print(x)
        x = x.strftime('%H:%M:%S')
        x_t = dt.strptime(str(x), '%H:%M:%S').time()
        print(x)
        if dt.combine(date.today(), x_t) > dt.combine(date.today(), t_time):
            z = dt.combine(date.today(), x_t) - dt.combine(date.today(), t_time)
            self.late = z.total_seconds() / 3600
            print("z = ", z.total_seconds() / 3600)
        if dt.combine(date.today(), x_t) < dt.combine(date.today(), t_time):
            z = dt.combine(date.today(), t_time) - dt.combine(date.today(), x_t)
            print("z = ", z.total_seconds() / 3600)
            self.late = z.total_seconds() / 3600

    def compute_early_late(self):
        # for check in
        check_in = self.check_in
        user_tz = self.env.context.get('tz')
        real_date = pytz.UTC.localize(check_in).astimezone(timezone(user_tz)).replace(tzinfo=None)
        print("real", real_date)
        real_date_as_datetime = dt.strptime(str(real_date), '%Y-%m-%d %H:%M:%S').time()

        planned_check_in = dt(1988, 2, 19, int(self.employee_id.hour_from), 0, 0)
        planned_check_in = planned_check_in.strftime('%H:%M:%S')
        planned_check_in_as_datetime = dt.strptime(str(planned_check_in), '%H:%M:%S').time()
        if dt.combine(date.today(), planned_check_in_as_datetime) > dt.combine(date.today(), real_date_as_datetime):
            z = dt.combine(date.today(), planned_check_in_as_datetime) - dt.combine(date.today(), real_date_as_datetime)
            self.early_sign_in = z.total_seconds() / 3600
            print("early = ", z.total_seconds() / 3600)
        if dt.combine(date.today(), planned_check_in_as_datetime) < dt.combine(date.today(), real_date_as_datetime):
            z = dt.combine(date.today(), real_date_as_datetime) - dt.combine(date.today(), planned_check_in_as_datetime)
            print("late = ", z.total_seconds() / 3600)
            self.late = z.total_seconds() / 3600
        ######################################################################################################
#         for check out
        check_out = self.check_out
        user_tz = self.env.context.get('tz')
        check_out_real_date = pytz.UTC.localize(check_out).astimezone(timezone(user_tz)).replace(tzinfo=None)
        print("real", check_out_real_date)
        check_out_real_date_as_datetime = dt.strptime(str(check_out_real_date), '%Y-%m-%d %H:%M:%S').time()

        planned_check_out = dt(1988, 2, 19, int(self.employee_id.hour_to), 0, 0)
        planned_check_out = planned_check_out.strftime('%H:%M:%S')
        planned_check_out_as_datetime = dt.strptime(str(planned_check_out), '%H:%M:%S').time()
        if dt.combine(date.today(), planned_check_out_as_datetime) > dt.combine(date.today(), check_out_real_date_as_datetime):
            z = dt.combine(date.today(), planned_check_out_as_datetime) - dt.combine(date.today(), check_out_real_date_as_datetime)
            self.early_leave = z.total_seconds() / 3600
            print("early Sign out = ", z.total_seconds() / 3600)
        if dt.combine(date.today(), planned_check_out_as_datetime) < dt.combine(date.today(), check_out_real_date_as_datetime):
            z = dt.combine(date.today(), check_out_real_date_as_datetime) - dt.combine(date.today(), planned_check_out_as_datetime)
            print("sign out late = ", z.total_seconds() / 3600)
            self.over_time = z.total_seconds() / 3600

    def compute_early_late_shifts(self):
        # check what shift
        t = self.check_in
        print("check IN = ",t)
        t = dt.strptime(str(t), '%Y-%m-%d %H:%M:%S').date()
        hour_from = 0
        hour_to = 0
        print("T = ", t)
        for line in self.employee_id.shift_ids:
            if line.date_from <= t and line.date_to >= t:
                print("shift exist")
                hour_from = line.hour_from
                hour_to = line.hour_to
         #################################
                # for check in
                check_in = self.check_in
                user_tz = self.env.context.get('tz')
                real_date = pytz.UTC.localize(check_in).astimezone(timezone(user_tz)).replace(tzinfo=None)
                print("real", real_date)
                real_date_as_datetime = dt.strptime(str(real_date), '%Y-%m-%d %H:%M:%S').time()

                planned_check_in = dt(1988, 2, 19, int(hour_from), 0, 0)
                planned_check_in = planned_check_in.strftime('%H:%M:%S')
                planned_check_in_as_datetime = dt.strptime(str(planned_check_in), '%H:%M:%S').time()
                if dt.combine(date.today(), planned_check_in_as_datetime) > dt.combine(date.today(), real_date_as_datetime):
                    z = dt.combine(date.today(), planned_check_in_as_datetime) - dt.combine(date.today(),
                                                                                            real_date_as_datetime)
                    self.early_sign_in = z.total_seconds() / 3600
                    self.late = 0
                    self.is_computed = True
                    print("early = ", z.total_seconds() / 3600)
                if dt.combine(date.today(), planned_check_in_as_datetime) < dt.combine(date.today(), real_date_as_datetime):
                    z = dt.combine(date.today(), real_date_as_datetime) - dt.combine(date.today(),
                                                                                     planned_check_in_as_datetime)
                    print("late = ", z.total_seconds() / 3600)
                    self.late = z.total_seconds() / 3600
                    self.early_sign_in = 0
                    self.is_computed = True
                ######################################################################################################
                #         for check out
                check_out = self.check_out
                user_tz = self.env.context.get('tz')
                check_out_real_date = pytz.UTC.localize(check_out).astimezone(timezone(user_tz)).replace(tzinfo=None)
                print("real", check_out_real_date)
                check_out_real_date_as_datetime = dt.strptime(str(check_out_real_date), '%Y-%m-%d %H:%M:%S').time()

                planned_check_out = dt(1988, 2, 19, int(hour_to), 0, 0)
                planned_check_out = planned_check_out.strftime('%H:%M:%S')
                planned_check_out_as_datetime = dt.strptime(str(planned_check_out), '%H:%M:%S').time()
                if dt.combine(date.today(), planned_check_out_as_datetime) > dt.combine(date.today(),
                                                                                        check_out_real_date_as_datetime):
                    z = dt.combine(date.today(), planned_check_out_as_datetime) - dt.combine(date.today(),
                                                                                             check_out_real_date_as_datetime)
                    self.early_leave = z.total_seconds() / 3600
                    self.over_time = 0
                    print("early Sign out = ", z.total_seconds() / 3600)
                    self.is_computed = True
                if dt.combine(date.today(), planned_check_out_as_datetime) < dt.combine(date.today(),
                                                                                        check_out_real_date_as_datetime):
                    z = dt.combine(date.today(), check_out_real_date_as_datetime) - dt.combine(date.today(),
                                                                                               planned_check_out_as_datetime)
                    print("sign out late = ", z.total_seconds() / 3600)
                    self.over_time = z.total_seconds() / 3600
                    self.early_leave = 0
                    self.is_computed = True
                break
            else:
                # raise UserError(_("No shift found"))
                self.early_sign_in = 0
                self.late = 0
                self.early_leave = 0
                self.over_time = 0
                self.is_computed = False

    def recompute_early_late_shifts(self):
        # search for non compute attendance records
        recs = self.search([('is_computed', '=', False)])
        if recs:
            for rec in recs:
                # check what shift
                t = rec.check_in
                t = dt.strptime(str(t), '%Y-%m-%d %H:%M:%S').date()
                hour_from = 0
                hour_to = 0
                for line in rec.employee_id.shift_ids:
                    if line.date_from <= t and line.date_to >= t:
                        print("shift exist")
                        hour_from = line.hour_from
                        hour_to = line.hour_to
                 #################################
                        # for check in
                        check_in = rec.check_in
                        user_tz = rec.env.context.get('tz')
                        real_date = pytz.UTC.localize(check_in).astimezone(timezone(user_tz)).replace(tzinfo=None)
                        print("real", real_date)
                        real_date_as_datetime = dt.strptime(str(real_date), '%Y-%m-%d %H:%M:%S').time()

                        planned_check_in = dt(1988, 2, 19, int(hour_from), 0, 0)
                        planned_check_in = planned_check_in.strftime('%H:%M:%S')
                        planned_check_in_as_datetime = dt.strptime(str(planned_check_in), '%H:%M:%S').time()
                        if dt.combine(date.today(), planned_check_in_as_datetime) > dt.combine(date.today(), real_date_as_datetime):
                            z = dt.combine(date.today(), planned_check_in_as_datetime) - dt.combine(date.today(),
                                                                                                    real_date_as_datetime)
                            rec.early_sign_in = z.total_seconds() / 3600
                            rec.late = 0
                            rec.is_computed = True
                            print("early = ", z.total_seconds() / 3600)
                        if dt.combine(date.today(), planned_check_in_as_datetime) < dt.combine(date.today(), real_date_as_datetime):
                            z = dt.combine(date.today(), real_date_as_datetime) - dt.combine(date.today(),
                                                                                             planned_check_in_as_datetime)
                            print("late = ", z.total_seconds() / 3600)
                            rec.late = z.total_seconds() / 3600
                            rec.early_sign_in = 0
                            rec.is_computed = True
                        ######################################################################################################
                        #         for check out
                        check_out = rec.check_out
                        user_tz = rec.env.context.get('tz')
                        check_out_real_date = pytz.UTC.localize(check_out).astimezone(timezone(user_tz)).replace(tzinfo=None)
                        print("real", check_out_real_date)
                        check_out_real_date_as_datetime = dt.strptime(str(check_out_real_date), '%Y-%m-%d %H:%M:%S').time()

                        planned_check_out = dt(1988, 2, 19, int(hour_to), 0, 0)
                        planned_check_out = planned_check_out.strftime('%H:%M:%S')
                        planned_check_out_as_datetime = dt.strptime(str(planned_check_out), '%H:%M:%S').time()
                        if dt.combine(date.today(), planned_check_out_as_datetime) > dt.combine(date.today(),
                                                                                                check_out_real_date_as_datetime):
                            z = dt.combine(date.today(), planned_check_out_as_datetime) - dt.combine(date.today(),
                                                                                                     check_out_real_date_as_datetime)
                            rec.early_leave = z.total_seconds() / 3600
                            rec.over_time = 0
                            print("early Sign out = ", z.total_seconds() / 3600)
                            rec.is_computed = True
                        if dt.combine(date.today(), planned_check_out_as_datetime) < dt.combine(date.today(),
                                                                                                check_out_real_date_as_datetime):
                            z = dt.combine(date.today(), check_out_real_date_as_datetime) - dt.combine(date.today(),
                                                                                                       planned_check_out_as_datetime)
                            print("sign out late = ", z.total_seconds() / 3600)
                            rec.over_time = z.total_seconds() / 3600
                            rec.early_leave = 0
                            rec.is_computed = True
                    else:
                        rec.early_sign_in = 0
                        rec.late = 0
                        rec.early_leave = 0
                        rec.over_time = 0
                        rec.is_computed = False
        else:
            raise UserError(_("no records found"))

    def compute_check_in_early_late(self):
        check_in = self.check_in
        user_tz = self.env.context.get('tz')
        real_date = pytz.UTC.localize(check_in).astimezone(timezone(user_tz)).replace(tzinfo=None)
        print("real", real_date)
        real_date_as_all = dt.strptime(str(real_date), '%Y-%m-%d %H:%M:%S')
        real_date_as_date = real_date_as_all.date()
        shift = []
        # what shift
        for line in self.employee_id.shift_ids:
            if line.date_from <= real_date_as_date and line.date_to >= real_date_as_date:
                print("shift exist")
                shift.append(line)
                print(shift)
        x = shift[0]
        print("x = ", x)
        print("From", x.hour_from)
        print("To", x.hour_to)
        if x:
            # for shift 8
            if x.hour_from == 8 and x.hour_to == 16:
                print("Hello Shift 8")
                h = real_date_as_all.hour  # get hour
                m = real_date_as_all.minute  # get hour
                if h == 8:
                    if m > 15:
                        self.late = m / 60
                    else:
                        self.late = 0
                if h > 8:
                    late_hours = h - 8
                    # late_minutes = m
                    self.late = late_hours + (m / 60)
                if h < 8:
                    early_hours = 7 - h  # (8 -1 = 7)
                    early_minutes = 60 - m
                    self.early_sign_in = early_hours + (early_minutes / 60)
            # for shift 16
            if x.hour_from == 16 and x.hour_to == 0:
                print("Hello Shift 16")
                h = real_date_as_all.hour  # get hour
                m = real_date_as_all.minute  # get hour
                if h == 16:
                    if m > 15:
                        self.late = m / 60
                    else:
                        self.late = 0
                if h > 16:
                    late_hours = h - 16
                    # late_minutes = m
                    self.late = late_hours + (m / 60)
                if h < 16:
                    early_hours = 15 - h  # (16 -1 = 15)
                    early_minutes = 60 - m
                    self.early_sign_in = early_hours + (early_minutes / 60)
            # for shift 00 evening
            if x.hour_from == 0 and x.hour_to == 8:
                print("Hello Shift 00")
                h = real_date_as_all.hour  # get hour
                m = real_date_as_all.minute  # get hour
                if h == 0:
                    if m > 15:
                        self.late = m / 60
                    else:
                        self.late = 0
                if h < 5:
                    late_hours = h
                    # late_minutes = m
                    self.late = late_hours + (m / 60)
                if h > 20:
                    early_hours = 23 - h  # (24 -1 = 23)
                    early_minutes = 60 - m
                    self.early_sign_in = early_hours + (early_minutes / 60)

    def compute_check_in_early_late_all(self):
        check_in = self.check_in
        user_tz = self.env.context.get('tz')
        real_date = pytz.UTC.localize(check_in).astimezone(timezone(user_tz)).replace(tzinfo=None)
        print("real", real_date)
        real_date_as_all = dt.strptime(str(real_date), '%Y-%m-%d %H:%M:%S')
        real_date_as_date = real_date_as_all.date()
        shift = []
        # what shift
        for line in self.employee_id.shift_ids:
            if line.date_from <= real_date_as_date and line.date_to >= real_date_as_date:
                print("shift exist")
                shift.append(line)
                print(shift)
        x = shift[0]
        print("x = ", x)
        print("From", x.hour_from)
        print("To", x.hour_to)
        if x:
            if x.hour_from != 0:
                print("Hello Shift ", x.hour_from)
                h = real_date_as_all.hour  # get hour
                m = real_date_as_all.minute  # get hour
                hour_from = x.hour_from
                if h == hour_from:
                    if m > 15:
                        self.late = m / 60
                    else:
                        self.late = 0
                if h > hour_from:
                    late_hours = h - hour_from
                    # late_minutes = m
                    self.late = late_hours + (m / 60)
                if h < hour_from:
                    early_hours = hour_from - h - 1  # (8 -1 = 7)
                    early_minutes = 60 - m
                    self.early_sign_in = early_hours + (early_minutes / 60)

            # for shift 00 evening
            if x.hour_from == 0:
                print("Hello Shift 00")
                h = real_date_as_all.hour  # get hour
                m = real_date_as_all.minute  # get hour

                if h == 0:
                    if m > 15:
                        self.late = m / 60
                    else:
                        self.late = 0
                if 0 > h < 5:
                    late_hours = h
                    # late_minutes = m
                    self.late = late_hours + (m / 60)
                if h > 20:
                    early_hours = 23 - h  # (24 -1 = 23)
                    early_minutes = 60 - m
                    self.early_sign_in = early_hours + (early_minutes / 60)

    def compute_check_in_early_late_all_big(self):
        attendances = self.env['hr.attendance'].search([('employee_id', '=', self.employee_id.id)])
        for atten in attendances:
            check_in = atten.check_in
            user_tz = atten.env.context.get('tz')
            real_date = pytz.UTC.localize(check_in).astimezone(timezone(user_tz)).replace(tzinfo=None)
            print("real", real_date)
            real_date_as_all = dt.strptime(str(real_date), '%Y-%m-%d %H:%M:%S')
            real_date_as_date = real_date_as_all.date()
            shift = []
            # what shift
            for line in atten.employee_id.shift_ids:
                if line.date_from <= real_date_as_date and line.date_to >= real_date_as_date:
                    print("shift exist")
                    shift.append(line)
                    print(shift)
            x = shift[0]
            print("x = ", x)
            print("From", x.hour_from)
            print("To", x.hour_to)
            if x:
                if x.hour_from != 0:
                    print("Hello Shift ", x.hour_from)
                    h = real_date_as_all.hour  # get hour
                    m = real_date_as_all.minute  # get hour
                    hour_from = x.hour_from
                    if h == hour_from:
                        if m > 15:
                            atten.late = m / 60
                        else:
                            atten.late = 0
                    if h > hour_from:
                        late_hours = h - hour_from
                        # late_minutes = m
                        atten.late = late_hours + (m / 60)
                    if h < hour_from:
                        early_hours = hour_from - h - 1  # (8 -1 = 7)
                        early_minutes = 60 - m
                        atten.early_sign_in = early_hours + (early_minutes / 60)

                # for shift 00 evening
                if x.hour_from == 0:
                    print("Hello Shift 00")
                    h = real_date_as_all.hour  # get hour
                    m = real_date_as_all.minute  # get hour

                    if h == 0:
                        if m > 15:
                            atten.late = m / 60
                        else:
                            atten.late = 0
                    if 0 > h < 5:
                        late_hours = h
                        # late_minutes = m
                        atten.late = late_hours + (m / 60)
                    if h > 20:
                        early_hours = 23 - h  # (24 -1 = 23)
                        early_minutes = 60 - m
                        atten.early_sign_in = early_hours + (early_minutes / 60)

    def compute_check_out_early_late(self):
        check_in = self.check_in
        user_tz = self.env.context.get('tz')
        real_date_check_in = pytz.UTC.localize(check_in).astimezone(timezone(user_tz)).replace(tzinfo=None)
        print("real", real_date_check_in)
        real_date_checkin_as_all = dt.strptime(str(real_date_check_in), '%Y-%m-%d %H:%M:%S')
        real_date_checkin_as_date = real_date_checkin_as_all.date()
        shift = []
        # what shift
        for line in self.employee_id.shift_ids:
            if line.date_from <= real_date_checkin_as_date and line.date_to >= real_date_checkin_as_date:
                print("shift exist")
                shift.append(line)
                print(shift)
        x = shift[0]
        print("x = ", x)
        print("From", x.hour_from)
        print("To", x.hour_to)

        # for check out
        check_out = self.check_out
        user_tz = self.env.context.get('tz')
        real_date_check_out = pytz.UTC.localize(check_out).astimezone(timezone(user_tz)).replace(tzinfo=None)
        print("real", real_date_check_out)
        real_date_checkout_as_all = dt.strptime(str(real_date_check_out), '%Y-%m-%d %H:%M:%S')

        if x:
            # for shift 8 - 16
            if x.hour_from == 8 and x.hour_to == 16:
                print("Hello Shift 8-16")
                h = real_date_checkout_as_all.hour  # get hour
                m = real_date_checkout_as_all.minute  # get hour
                if h == 16:
                    self.over_time = m / 60

                if h > 16:
                    over_time_hours = h - 16
                    # over_time__minutes = m
                    self.over_time = over_time_hours + (m / 60)
                if h < 16:
                    early_leave_hours = 15 - h  # (16 -1 = 15)
                    early_leave_minutes = 60 - m
                    self.early_leave = early_leave_hours + (early_leave_minutes / 60)
            # for shift 16 - 00
            if x.hour_from == 16 and x.hour_to == 0:
                print("Hello Shift 16-00")
                h = real_date_checkout_as_all.hour  # get hour
                m = real_date_checkout_as_all.minute  # get hour
                if h == 0:
                    self.over_time = m / 60
                if h > 0:
                    over_time_hours = h
                    # late_minutes = m
                    self.over_time = h + (m / 60)
                if h < 24:
                    early_leave_hours = 23 - h  # (24 -1 = 23)
                    early_leave_minutes = 60 - m
                    self.early_leave = early_leave_hours + (early_leave_minutes / 60)
            # for shift 00 - 08 evening
            if x.hour_from == 0 and x.hour_to == 8:
                print("Hello Shift 00 - 08")
                h = real_date_checkout_as_all.hour  # get hour
                m = real_date_checkout_as_all.minute  # get hour
                if h == 8:
                    self.over_time = m / 60
                if h > 8:
                    over_time_hours = h - 8
                    # late_minutes = m
                    self.over_time = over_time_hours + (m / 60)
                if h < 8:
                    early_leave_hours = 7 - h  # (8 -1 = 7)
                    early_leave_minutes = 60 - m
                    self.early_leave = early_leave_hours + (early_leave_minutes / 60)

    def compute_check_out_early_late_all(self):
        check_in = self.check_in
        user_tz = self.env.context.get('tz')
        real_date_check_in = pytz.UTC.localize(check_in).astimezone(timezone(user_tz)).replace(tzinfo=None)
        print("real", real_date_check_in)
        real_date_checkin_as_all = dt.strptime(str(real_date_check_in), '%Y-%m-%d %H:%M:%S')
        real_date_checkin_as_date = real_date_checkin_as_all.date()
        shift = []
        # what shift
        for line in self.employee_id.shift_ids:
            if line.date_from <= real_date_checkin_as_date and line.date_to >= real_date_checkin_as_date:
                print("shift exist")
                shift.append(line)
                print(shift)
        x = shift[0]
        print("x = ", x)
        print("From", x.hour_from)
        print("To", x.hour_to)

        # for check out
        check_out = self.check_out
        user_tz = self.env.context.get('tz')
        real_date_check_out = pytz.UTC.localize(check_out).astimezone(timezone(user_tz)).replace(tzinfo=None)
        print("real", real_date_check_out)
        real_date_checkout_as_all = dt.strptime(str(real_date_check_out), '%Y-%m-%d %H:%M:%S')

        if x:
            # for shift 8 - 16
            if x.hour_to != 0:
                print("Hello Shift ", x.hour_to)
                h = real_date_checkout_as_all.hour  # get hour
                m = real_date_checkout_as_all.minute  # get hour
                hour_to = x.hour_to
                if h == hour_to:
                    self.over_time = m / 60

                if h > hour_to:
                    over_time_hours = h - hour_to
                    # over_time__minutes = m
                    self.over_time = over_time_hours + (m / 60)
                if h < hour_to:
                    early_leave_hours = hour_to - h - 1  # (16 -1 = 15)
                    early_leave_minutes = 60 - m
                    self.early_leave = early_leave_hours + (early_leave_minutes / 60)
            # for shift 16 - 00
            if x.hour_to == 0:
                print("Hello Shift 16-00")
                h = real_date_checkout_as_all.hour  # get hour
                m = real_date_checkout_as_all.minute  # get hour
                hour_to = x.hour_to
                if h == 0:
                    self.over_time = m / 60
                if 0 < h and h < 5:
                    over_time_hours = h
                    # late_minutes = m
                    self.over_time = h + (m / 60)
                if h > 20:
                    early_leave_hours = 23 - h  # (24 -1 = 23)
                    early_leave_minutes = 60 - m
                    self.early_leave = early_leave_hours + (early_leave_minutes / 60)

    def compute_check_out_early_late_all_big(self):
        attendances = self.env['hr.attendance'].search([('employee_id', '=', self.employee_id.id)])
        for atten in attendances:
            check_in = atten.check_in
            user_tz = atten.env.context.get('tz')
            real_date_check_in = pytz.UTC.localize(check_in).astimezone(timezone(user_tz)).replace(tzinfo=None)
            print("real", real_date_check_in)
            real_date_checkin_as_all = dt.strptime(str(real_date_check_in), '%Y-%m-%d %H:%M:%S')
            real_date_checkin_as_date = real_date_checkin_as_all.date()
            shift = []
            # what shift
            for line in atten.employee_id.shift_ids:
                if line.date_from <= real_date_checkin_as_date and line.date_to >= real_date_checkin_as_date:
                    print("shift exist")
                    shift.append(line)
                    print(shift)
            x = shift[0]
            print("x = ", x)
            print("From", x.hour_from)
            print("To", x.hour_to)

            # for check out
            check_out = atten.check_out
            user_tz = atten.env.context.get('tz')
            real_date_check_out = pytz.UTC.localize(check_out).astimezone(timezone(user_tz)).replace(tzinfo=None)
            print("real", real_date_check_out)
            real_date_checkout_as_all = dt.strptime(str(real_date_check_out), '%Y-%m-%d %H:%M:%S')

            if x:
                # for shift 8 - 16
                if x.hour_to != 0:
                    print("Hello Shift ", x.hour_to)
                    h = real_date_checkout_as_all.hour  # get hour
                    m = real_date_checkout_as_all.minute  # get hour
                    hour_to = x.hour_to
                    if h == hour_to:
                        atten.over_time = m / 60

                    if h > hour_to:
                        over_time_hours = h - hour_to
                        # over_time__minutes = m
                        atten.over_time = over_time_hours + (m / 60)
                    if h < hour_to:
                        early_leave_hours = hour_to - h - 1  # (16 -1 = 15)
                        early_leave_minutes = 60 - m
                        atten.early_leave = early_leave_hours + (early_leave_minutes / 60)
                # for shift 16 - 00
                if x.hour_to == 0:
                    print("Hello Shift 16-00")
                    h = real_date_checkout_as_all.hour  # get hour
                    m = real_date_checkout_as_all.minute  # get hour
                    hour_to = x.hour_to
                    if h == 0:
                        atten.over_time = m / 60
                    if 0 < h and h < 5:
                        over_time_hours = h
                        # late_minutes = m
                        atten.over_time = h + (m / 60)
                    if h > 20:
                        early_leave_hours = 23 - h  # (24 -1 = 23)
                        early_leave_minutes = 60 - m
                        atten.early_leave = early_leave_hours + (early_leave_minutes / 60)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # hour_from = fields.Float(string="Hour From")
    # hour_to = fields.Float(string="Hour To")
    shift_ids = fields.One2many('employee.shift.line', 'employee_id')


class EmployeeShiftLine(models.Model):
    _name = 'employee.shift.line'

    employee_id = fields.Many2one('hr.employee')
    name = fields.Char(string="Shift Name")
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date TO")
    hour_from = fields.Float(string="Hour From")
    hour_to = fields.Float(string="Hour To")





