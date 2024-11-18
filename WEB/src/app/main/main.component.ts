import { Component } from '@angular/core';

@Component({
  selector: 'app-main',
  standalone: true,
  imports: [],
  templateUrl: './main.component.html',
  styleUrl: './main.component.css'
})

export class MainComponent {

  content:string = "";

  ngAfterViewInit(): void {
    const input = document.getElementById('pregunta') as HTMLInputElement;
    const button = document.getElementById('preguntar') as HTMLButtonElement;


    if (button) {
      button.onclick = () => this.responder();
    }
  
    
  
  }

  responder(): void {

    this.content = "hola";

  }


}
