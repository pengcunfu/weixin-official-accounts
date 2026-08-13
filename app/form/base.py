from flask_wtf import FlaskForm


class BaseForm(FlaskForm):
    class Meta:
        csrf = False  # 禁用CSRF保护，适用于API接口

    def get_first_error(self):
        if self.errors:
            for field, errors in self.errors.items():
                return errors[0]
        return None
