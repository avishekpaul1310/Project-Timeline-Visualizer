from django import forms
from django.core.exceptions import ValidationError
from .models import Project, Milestone
from django.contrib.auth.models import User

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
        fields = ['name', 'due_date', 'status', 'description', 'dependencies']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)
        
        # Limit dependencies to milestones within the same project
        # Exclude the current milestone if we're editing
        if self.project:
            milestone_queryset = Milestone.objects.filter(project=self.project)
            if self.instance.pk:
                milestone_queryset = milestone_queryset.exclude(pk=self.instance.pk)
            self.fields['dependencies'].queryset = milestone_queryset
            self.fields['dependencies'].label = "Depends on (milestones that must be completed first)"
            self.fields['dependencies'].widget = forms.CheckboxSelectMultiple()

    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        project = self.project  # Use the project passed in __init__

        if project and due_date:
            if due_date < project.start_date or due_date > project.end_date:
                raise ValidationError(
                    "Milestone due date must be within project start and end dates"
                )
        return due_date
    
class ProjectShareForm(forms.Form):
    email = forms.EmailField(label="Collaborator's email")
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("No user with this email address was found.")
        return email