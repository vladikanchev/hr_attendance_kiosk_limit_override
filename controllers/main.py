from datetime import datetime, time
from odoo import http
from odoo.http import request

class KioskAttendanceCustom(http.Controller):

    @http.route('/hr_attendance/attendance_scan', type='json', auth='user')
    def attendance_scan(self, barcode=None, employee_id=None, mode='manual'):
        employee = None
        if barcode:
            employee = request.env['hr.employee'].sudo().search([('barcode', '=', barcode)], limit=1)
        elif employee_id:
            employee = request.env['hr.employee'].sudo().browse(employee_id)

        if not employee:
            return {'error': 'Invalid badge ID or employee'}

        now = datetime.now()
        today = now.date()
        fifteen_pm = time(15, 0, 0)

        attendance = request.env['hr.attendance'].sudo().search([
            ('employee_id', '=', employee.id),
            ('check_in', '>=', datetime.combine(today, time.min)),
            ('check_in', '<=', datetime.combine(today, time.max))
        ], order='check_in desc', limit=1)

        if now.time() < fifteen_pm:
            if attendance and not attendance.check_out:
                return {'warning': 'Вече сте се чекирали.'}
            if attendance and attendance.check_out:
                return {'warning': 'Вече сте се чекирали и отписали за днес.'}
            request.env['hr.attendance'].sudo().create({
                'employee_id': employee.id,
                'check_in': now,
            })
            return {'success': 'Чек-ин записан успешно'}
        else:
            if attendance and not attendance.check_out:
                attendance.write({'check_out': now})
                return {'success': 'Чек-аут записан успешно'}
            elif attendance and attendance.check_out:
                return {'warning': 'Вече сте се отписали.'}
            else:
                return {'warning': 'Няма чек-ин за днес. Не можете да се отпишете.'}
