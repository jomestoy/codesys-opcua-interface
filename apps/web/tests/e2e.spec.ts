import { expect, test } from "@playwright/test";

test("Inicio de sesión y navegación principal", async ({ page }) => {
  await page.route("**/api/auth/demo-credentials", async (route) => {
    await route.fulfill({ json: { admin: "AdminTemporal!2026" } });
  });
  await page.route("**/api/auth/login", async (route) => {
    await route.fulfill({
      json: {
        access_token: "demo-token",
        user: {
          id: "admin",
          username: "admin",
          display_name: "Administrador",
          active: true,
          password_change_required: false,
          profile_photo_url: "",
          role: { id: "admin", name: "Administrador", permissions: ["*"] }
        }
      }
    });
  });
  await page.route("**/api/system/summary", async (route) => {
    await route.fulfill({
      json: {
        columns_total: 200,
        running: 20,
        paused: 0,
        alarm: 1,
        offline: 0,
        available: 179,
        active_campaigns: 1,
        flow_total_kg_h: 240,
        data_quality: 0.96,
        real_io_enabled: false,
        critical_alarms: 1,
        gateways: [{ gateway_id: "GW-DEMO-01", online: true, quality: 0.96 }],
        codesys: {
          primary: { controller_id: "CODESYS-A", role: "primary", active: true, healthy: true },
          secondary: { controller_id: "CODESYS-B", role: "secondary", active: false, healthy: true }
        }
      }
    });
  });
  await page.route("**/api/integrations", async (route) => {
    await route.fulfill({
      json: {
        grafana: {
          enabled: true,
          base_path: "/grafana/",
          control_allowed: false,
          dashboards: [{ uid: "column-overview", title: "Columnas - resumen operacional", panels: 7, editable: false, path: "grafana/dashboards/column-overview.json", tags: ["readonly"] }]
        },
        node_red: {
          enabled: true,
          runtime_base_path: "/node-red/",
          admin_base_path: "/node-red-admin/",
          control_allowed: false,
          flows: [{ id: "notifications-flow", label: "Notificaciones y reportes", disabled: false, contains_control_keywords: false, path: "node-red/flows/notifications.json" }]
        }
      }
    });
  });

  await page.goto("/");
  await page.getByRole("button", { name: "Usar demo" }).click();
  await page.getByRole("button", { name: "Ingresar" }).click();
  await expect(page.getByText("BV Column Control")).toBeVisible();
  await page.getByRole("tab", { name: "Integraciones" }).click();
  await expect(page.getByText("Grafana")).toBeVisible();
  await expect(page.getByText("Node-RED")).toBeVisible();
});
