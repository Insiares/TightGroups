import flet as ft

def main(page: ft.Page):
    # Configure page
    page.title = "My Shooting App"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # Create UI components
    def create_setup_view():
        # Your setup creation logic
        name_input = ft.TextField(label="Setup Name")
        gear_input = ft.TextField(label="Gear")
        
        def save_setup(e):
            # Save logic here
            print(f"Saving setup: {name_input.value}")

        save_button = ft.ElevatedButton("Save Setup", on_click=save_setup)
        
        return ft.Column([
            name_input,
            gear_input,
            save_button
        ])

    def create_seance_view():
        # Seance (shooting session) creation
        date_picker = ft.DatePicker()
        
        location_button = ft.ElevatedButton(
            "Get Location", 
            on_click=lambda e: print("Getting location...")
        )
        
        return ft.Column([
            ft.Text("Create New Shooting Session"),
            date_picker,
            location_button
        ])

    # Create bottom navigation
    def create_bottom_nav():
        return ft.NavigationBar(
            destinations=[
                ft.NavigationDestination(icon=ft.icons.SETTINGS, label="Setups"),
                ft.NavigationDestination(icon=ft.icons.CAMERA, label="Seances"),
                ft.NavigationDestination(icon=ft.icons.ANALYTICS, label="Analytics")
            ]
        )

    # Main app layout
    page.add(
        ft.Column([
            ft.Text("Shooting Companion App", size=24, weight=ft.FontWeight.BOLD),
            create_setup_view(),
            create_seance_view(),
            create_bottom_nav()
        ])
    )

# Run the app
ft.app(target=main)
