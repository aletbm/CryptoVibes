resource "google_bigquery_dataset" "raw" {
  dataset_id = "raw"
  location   = var.region
  delete_contents_on_destroy = true
}

resource "google_bigquery_dataset" "staging" {
  dataset_id = "staging"
  location   = var.region
  delete_contents_on_destroy = true
}

resource "google_bigquery_dataset" "intermediate" {
  dataset_id = "intermediate"
  location   = var.region
  delete_contents_on_destroy = true
}

resource "google_bigquery_dataset" "marts" {
  dataset_id = "marts"
  location   = var.region
  delete_contents_on_destroy = true
}
