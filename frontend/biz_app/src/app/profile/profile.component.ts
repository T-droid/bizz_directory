import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-profile',
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.css']
})
export class ProfileComponent implements OnInit {
  username: string = 'John Doe'; // Replace with actual username
  enrolledPrograms: string[] = ['Strength Training', 'Yoga']; // Example of enrolled programs

  constructor() { }

  ngOnInit(): void {
    // You can fetch the enrolled programs for the user from a service or API
  }
}
