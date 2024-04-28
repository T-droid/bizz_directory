import { Component } from '@angular/core';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent {
  categories = [
    { name: 'Strength Training', fitnessTypes: ['Weightlifting', 'Bodyweight Exercises', 'Powerlifting', 'CrossFit'] },
    { name: 'Cardio', fitnessTypes: ['Running', 'Cycling', 'Jump Rope', 'HIIT'] },
    { name: 'Yoga', fitnessTypes: ['Hatha Yoga', 'Vinyasa Yoga', 'Ashtanga Yoga', 'Yin Yoga'] }
    // Add more categories and fitness types as needed
  ];
}
