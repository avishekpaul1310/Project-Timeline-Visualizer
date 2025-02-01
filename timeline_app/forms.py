from django import forms
from django.core.exceptions import ValidationError
from .models import Project, Milestone

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if end_date < start_date:
                raise ValidationError("End date cannot be before start date")
        return cleaned_data

class MilestoneForm(forms.ModelForm):
    class Meta:
        model = Milestone
        fields = ['name', 'due_date']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)

    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        project = self.project or (self.instance.project if self.instance else None)

        if project and due_date:
            if due_date < project.start_date or due_date > project.end_date:
                raise ValidationError(
                    "Milestone due date must be within project start and end dates"
                )
        return due_date

    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        project = self.instance.project if self.instance else None

        if project and due_date:
            if due_date < project.start_date or due_date > project.end_date:
                raise ValidationError(
                    "Milestone due date must be within project start and end dates"
                )
        return due_date