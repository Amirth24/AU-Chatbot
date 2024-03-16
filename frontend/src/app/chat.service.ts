import { Injectable } from '@angular/core';
import {Observable, of} from 'rxjs'

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private socket: WebSocket | null = null;
  private _messList: string[] = [];
  public messages$: Observable<any>| null = null;
  private _currentMessage: string = "";
  constructor() {}
  init(url: string) {
    this.socket = new WebSocket(url);
    this.socket.onopen = (e) => {
      console.log("Joined Chat");
      console.log(e);
    }

    this.messages$ = new Observable((subscriber) => {
      subscriber.next(this._messList);

      if (this.socket !== null){
        this.socket.onmessage = (e) => {
          console.log(e.data);
          this._currentMessage += e.data;
          if (this._currentMessage.endsWith('[END]')){
            this._messList = [
              ...this._messList,this._currentMessage.slice(0, -5)];
            subscriber.next(this._messList)
            this._currentMessage="";
          }
        }
      }

    });
  }

  sendMsg(mess: string){
    this.socket?.send(mess);
    console.log("Message Sent " + mess);
  }
}
