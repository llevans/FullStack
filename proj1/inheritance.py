class Parent():
      def __init__(self, last_name, eye_color):
         print("Parent constructor called")
         self.last_name = last_name
         self.eye_color = eye_color

      def show_info(self):
         print(self.last_name)
         print(self.eye_color)

class Child(Parent):
      def __init__(self, last_name, eye_color, number_of_toys):
         print("Child constructor called")
         Parent.__init__(self, last_name, eye_color)
         self.number_of_toys = number_of_toys
    
miley = Child("Cyrus", "blue", 5)
miley.show_info()
